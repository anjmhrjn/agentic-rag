# agents/evaluator.py

import re
import logging
from typing import Dict, List, Optional, Tuple
from llm.local_llm import LocalLLM

class AnswerEvaluator:
    """
    Evaluates answer quality and detects issues like hallucinations,
    invalid citations, and irrelevant responses.
    """
    
    def __init__(self, llm: LocalLLM):
        self.llm = llm
        self.logger = logging.getLogger(__name__)
        
        # Quality thresholds
        self.MIN_QUALITY_SCORE = 0.6  # Below this, trigger re-generation
        self.CITATION_WEIGHT = 0.3
        self.RELEVANCE_WEIGHT = 0.4
        self.SUPPORT_WEIGHT = 0.3
    
    def evaluate(
        self,
        query: str,
        answer: str,
        sources: List[str],
        context_chunks: List[Dict]
    ) -> Dict:
        """
        Comprehensive answer evaluation.
        
        Args:
            query: Original user query
            answer: Generated answer
            sources: List of cited doc_ids
            context_chunks: Retrieved context used for generation
        
        Returns:
            Dict with quality_score, issues, and recommendations
        """
        self.logger.info(f"Evaluating answer for query: {query[:50]}...")
        
        # Check 1: Citation Validity
        citation_score, citation_issues = self._check_citations(answer, sources, context_chunks)
        
        # Check 2: Answer Relevance
        relevance_score, relevance_issues = self._check_relevance(query, answer)
        
        # Check 3: Contextual Support (Hallucination Detection)
        support_score, support_issues = self._check_contextual_support(answer, context_chunks)
        
        # Calculate overall quality score
        quality_score = (
            self.CITATION_WEIGHT * citation_score +
            self.RELEVANCE_WEIGHT * relevance_score +
            self.SUPPORT_WEIGHT * support_score
        )
        
        # Aggregate issues
        all_issues = citation_issues + relevance_issues + support_issues
        
        # Determine if re-generation is needed
        needs_regeneration = quality_score < self.MIN_QUALITY_SCORE
        
        result = {
            "quality_score": round(quality_score, 3),
            "citation_score": round(citation_score, 3),
            "relevance_score": round(relevance_score, 3),
            "support_score": round(support_score, 3),
            "issues": all_issues,
            "needs_regeneration": needs_regeneration,
            "recommendation": self._get_recommendation(quality_score, all_issues)
        }
        
        self.logger.info(f"Evaluation complete: quality={quality_score:.3f}, needs_regen={needs_regeneration}")
        return result
    
    def _check_citations(
        self,
        answer: str,
        sources: List[str],
        context_chunks: List[Dict]
    ) -> Tuple[float, List[str]]:
        """
        Check if citations in answer are valid.
        """
        issues = []
        
        # Extract cited doc_ids from answer (e.g., [DOC-123])
        cited_docs = re.findall(r'\[([A-Z]+-\d+)\]', answer)
        
        if not cited_docs:
            # No citations found
            if len(answer) > 100:  # Only penalize substantial answers
                issues.append("No citations found in answer")
                return 0.5, issues  # Partial score
            return 1.0, issues  # Short answers might not need citations
        
        # Check if cited docs are in actual sources
        valid_source_ids = set(sources)
        invalid_citations = []
        
        for cited_doc in cited_docs:
            if cited_doc not in valid_source_ids:
                invalid_citations.append(cited_doc)
        
        if invalid_citations:
            issues.append(f"Invalid citations (not in sources): {invalid_citations}")
            score = 1.0 - (len(invalid_citations) / len(cited_docs))
        else:
            score = 1.0
        
        return max(score, 0.0), issues
    
    def _check_relevance(self, query: str, answer: str) -> Tuple[float, List[str]]:
        """
        Check if answer is relevant to the query using LLM.
        """
        issues = []
        
        # Quick heuristic checks first
        if len(answer) < 20:
            issues.append("Answer is too short")
            return 0.3, issues
        
        if "i don't know" in answer.lower() or "no information" in answer.lower():
            issues.append("Answer admits lack of knowledge")
            return 0.4, issues
        
        # Use LLM to evaluate relevance
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are an answer quality evaluator. Determine if an answer is relevant to the question.
Output ONLY valid JSON: {{"relevant": true/false, "reason": "brief explanation"}}
<|eot_id|><|start_header_id|>user<|end_header_id|>

Question: {query}

Answer: {answer}

Is this answer relevant to the question? Output format:
{{"relevant": true, "reason": "..."}}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        
        try:
            response = self.llm.generate(prompt)
            import json
            evaluation = json.loads(response.strip())
            
            is_relevant = evaluation.get("relevant", True)
            reason = evaluation.get("reason", "")
            
            if not is_relevant:
                issues.append(f"Answer not relevant: {reason}")
                return 0.2, issues
            
            return 1.0, issues
        
        except Exception as e:
            self.logger.warning(f"Relevance check failed: {e}, assuming relevant")
            return 0.8, issues  # Default to mostly relevant if check fails
    
    def _check_contextual_support(
        self,
        answer: str,
        context_chunks: List[Dict]
    ) -> Tuple[float, List[str]]:
        """
        Check if answer is supported by the retrieved context.
        Detects hallucinations.
        """
        issues = []
        
        if not context_chunks:
            issues.append("No context available to verify answer")
            return 0.5, issues
        
        # Combine all context
        full_context = self._format_context(context_chunks)
        
        # Use LLM to check if answer is supported by context
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a fact-checker. Determine if an answer is supported by the given context.
Check for hallucinations - claims not present in the context.
Output ONLY valid JSON: {{"supported": true/false, "hallucinations": ["list", "of", "unsupported", "claims"]}}
<|eot_id|><|start_header_id|>user<|end_header_id|>

Context:
{full_context[:2000]}  

Answer to verify:
{answer}

Is this answer fully supported by the context? List any unsupported claims.
Output format:
{{"supported": true, "hallucinations": []}}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        
        try:
            response = self.llm.generate(prompt)
            import json
            evaluation = json.loads(response.strip())
            
            is_supported = evaluation.get("supported", True)
            hallucinations = evaluation.get("hallucinations", [])
            
            if not is_supported or hallucinations:
                issues.append(f"Possible hallucinations detected: {hallucinations}")
                score = 1.0 - (len(hallucinations) * 0.2)  # -0.2 per hallucination
                return max(score, 0.0), issues
            
            return 1.0, issues
        
        except Exception as e:
            self.logger.warning(f"Support check failed: {e}, assuming supported")
            return 0.8, issues  # Default to mostly supported if check fails
    
    def _get_recommendation(self, quality_score: float, issues: List[str]) -> str:
        """Generate recommendation based on evaluation"""
        if quality_score >= 0.9:
            return "Excellent quality - use this answer"
        elif quality_score >= 0.7:
            return "Good quality - minor issues detected"
        elif quality_score >= 0.6:
            return "Acceptable quality - consider improvement"
        else:
            return f"Poor quality - regenerate with different strategy. Issues: {'; '.join(issues)}"

    def _format_context(self, chunks: List[Dict]) -> str:
        """Format retrieved chunks into context string"""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            doc_id = chunk.get("doc_id", "UNKNOWN")
            text = chunk.get("text", "")
            doc_type = chunk.get("doc_type", [])
            score = chunk.get("similarity_score", 0.0)
            
            context_parts.append(
                f"[{doc_id}] (relevance: {score:.2f}, type: {', '.join(doc_type)})\n{text}\n"
            )
        
        return "\n---\n".join(context_parts)


# ==================== Usage Example ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    from llm.local_llm import LocalLLM
    
    llm = LocalLLM(model_path="models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf")
    evaluator = AnswerEvaluator(llm)
    
    # Test case 1: Good answer
    query = "What is the specific command and flag required to scale the RDS cluster immediately during a high-traffic event?"
    answer = "aws rds modify-db-instance --db-instance-identifier retail-prod-db --db-instance-class db.r5.large --apply-immediately [KB-017]"
    sources = ["KB-017"]
    context = [
        {"doc_id": "KB-017", "text": "### KB-017: Runbook: PostgreSQL RDS Cluster Scaling\n#### Objective\n\nProvides step-by-step instructions for increasing database capacity when indexFullness or CPU thresholds are exceeded.\n\n#### When to Use\n\nUse this when the Prometheus alert db\\_cpu\\_high triggers or when preparing for a high-traffic event (e.g., Black Friday).\n\n#### Preconditions\n\n- AWS CLI configured with DatabaseAdmin permissions.\n- The database must be in a Available state.\n\n#### Step-by-Step Instructions\n\n1. Identify the current instance class:\naws rds describe-db-instances --db-instance-identifier retail-prod-db\n2. Apply the new instance type (e.g., moving from db.t3.medium to db.r5.large):\naws rds modify-db-instance --db-instance-identifier retail-prod-db --db-instance-class db.r5.large --apply-immediately\n3. Monitor the \"Status\" field. It will move to modifying.\n\n#### Validation Steps\n\n1. Verify the new class is active:\naws rds describe-db-instances... --query 'DBInstances.DBInstanceClass'\n2. Confirm that the Order Service (KB-006) latency has returned to the baseline (&lt;200ms).\n\n#### Decisions &amp; Reasoning\n\n- **Decision:** Use of --apply-immediately for capacity-related scaling.\n- **Reasoning:** By default, RDS applies changes during the next maintenance window. If we are under active load pressure, we cannot wait for the weekend. While this causes a brief (30-60 second) failover/reboot, it is preferable to a sustained multi-hour slowdown that affects 100% of users."},
    ]
    
    result = evaluator.evaluate(query, answer, sources, context)
    print("\nTest 1 - Good Answer:")
    print(f"Quality: {result['quality_score']}")
    print(f"Issues: {result['issues']}")
    print(f"Recommendation: {result['recommendation']}")
    
    # Test case 2: Hallucinated citation
    answer_bad = "To scale pods, consult [DOC-999] which doesn't exist."
    result = evaluator.evaluate(query, answer_bad, sources, context)
    print("\nTest 2 - Hallucinated Citation:")
    print(f"Quality: {result['quality_score']}")
    print(f"Issues: {result['issues']}")
    print(f"Needs regeneration: {result['needs_regeneration']}")