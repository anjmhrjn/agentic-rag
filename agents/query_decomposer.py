# agents/query_decomposer.py

import json
import logging
from typing import List, Dict, Optional
from llm.local_llm import LocalLLM

class QueryDecomposerAgent:
    """
    Decomposes complex queries into simpler sub-queries.
    """
    
    def __init__(self, llm: LocalLLM):
        self.llm = llm
        self.logger = logging.getLogger(__name__)
    
    def should_decompose(self, query: str) -> bool:
        """
        Determine if query needs decomposition.
        """
        query_lower = query.lower()
        
        # Indicators of multi-part questions
        multi_part_indicators = [
            ' and ', ' or ', ' also ',
            'compare', 'difference between', 'versus', 'vs',
            'both', 'either',
            'as well as',
            'additionally',
            'furthermore'
        ]
        
        # Check for multiple questions
        has_multiple_questions = query.count('?') > 1
        
        # Check for multi-part indicators
        has_multi_part = any(indicator in query_lower for indicator in multi_part_indicators)
        
        # Check for multiple verbs (rough heuristic)
        action_words = ['how', 'what', 'why', 'when', 'where', 'explain', 'describe', 'show']
        action_count = sum(1 for word in action_words if word in query_lower)
        
        return has_multiple_questions or (has_multi_part and action_count >= 2)
    
    def decompose(self, query: str) -> List[str]:
        """
        Decompose query into sub-queries.
        Returns list of sub-queries, or [original_query] if no decomposition needed.
        """
        if not self.should_decompose(query):
            self.logger.info("Query doesn't need decomposition")
            return [query]
        
        self.logger.info(f"Decomposing query: {query}")
        
        prompt = self._build_decomposition_prompt(query)
        response = self.llm.generate(prompt)
        
        sub_queries = self._extract_sub_queries(response, query)
        
        self.logger.info(f"Decomposed into {len(sub_queries)} sub-queries: {sub_queries}")
        return sub_queries
    
    def _build_decomposition_prompt(self, query: str) -> str:
        """Build prompt for query decomposition"""
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You break complex questions into simpler sub-questions.

STRICT RULES:
1. Each sub-question MUST be fully self-contained with ALL context from the original
2. NEVER drop specific details (names, numbers, technologies, conditions)
3. ONLY generate sub-questions that are explicitly asked or directly implied
4. Do NOT invent new questions that weren't in the original
5. Cover ALL questions asked in the original - missing one is a failure
6. Each sub-question must make sense WITHOUT reading the original
7. Instead of using pronouns like "it", "they", "this", repeat the specific subject in every sub-question

CONTEXT PRESERVATION RULE:
If original mentions a specific condition or system, every sub-question
related to it MUST repeat that condition or system explicitly.

BAD EXAMPLE (loses context):
Original: "Our load balancer is dropping 2 percent of requests during peak hours. Is this normal? How do we fix it?"
Bad decomposition:
- "Is a 2 percent drop rate normal?" ← Missing "load balancer" and "peak hours" context
- "How do we fix the issue?" ← Too vague, missing all context
- "What causes request drops?" ← NEVER ASKED, hallucinated

GOOD EXAMPLE (preserves context):
Good decomposition:
- "Is it normal for a load balancer to drop 2 percent of requests during peak hours?"
- "How do we fix a load balancer that is dropping 2 percent of requests during peak hours?"

ANOTHER GOOD EXAMPLE:
Original: "How do I scale Kubernetes pods and monitor their performance?"
Good decomposition:
- "How do I scale Kubernetes pods?"
- "How do I monitor the performance of Kubernetes pods?"

Output ONLY valid JSON:
{{"sub_queries": ["full self-contained question 1", "full self-contained question 2"]}}
<|eot_id|><|start_header_id|>user<|end_header_id|>

Original Question: "{query}"

Rules reminder:
- Keep ALL specific details in EVERY sub-question
- Cover EVERY question asked
- Do NOT add questions not in the original

Break this into 2-4 sub-questions. Output format:
{{"sub_queries": ["...", "..."]}}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        return prompt
    
    def _extract_sub_queries(self, response: str, original_query: str) -> List[str]:
        """Extract sub-queries from LLM response"""
        try:
            # Clean response
            cleaned = response.strip()
            if cleaned.startswith('```'):
                cleaned = cleaned.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            parsed = json.loads(cleaned)
            sub_queries = parsed.get("sub_queries", [])
            
            # Validate
            if not sub_queries or not isinstance(sub_queries, list):
                self.logger.warning("Invalid sub_queries format, using original query")
                return [original_query]
            
            # Filter out empty strings
            sub_queries = [q.strip() for q in sub_queries if q.strip()]

            # Sub-queries should carry context, so should be reasonably long
            sub_queries = [
                q for q in sub_queries 
                if len(q.split()) >= 5  # Filter out vague 2-3 word queries
            ]
            
            # Limit to 4 sub-queries max
            if len(sub_queries) > 4:
                self.logger.warning(f"Too many sub-queries ({len(sub_queries)}), limiting to 4")
                sub_queries = sub_queries[:4]

            if len(sub_queries) <= 1:
                self.logger.warning("Decomposition produced 1 or fewer sub-queries, using original")
                return [original_query]
            
            return sub_queries if sub_queries else [original_query]
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse decomposition response: {e}")
            return [original_query]
        except Exception as e:
            self.logger.error(f"Error extracting sub-queries: {e}")
            return [original_query]


# ==================== Usage Example ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    from llm.local_llm import LocalLLM
    
    llm = LocalLLM(model_path="models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf")
    decomposer = QueryDecomposerAgent(llm)
    
    test_queries = [
        "How do I restart a pod?",  # Simple - no decomposition
        "A feature flag has been enabled in production for 18 months. What should happen next and why?",  # Complex
        "You notice Redis memory at 76 percent during normal traffic. What actions should you take and why?",
        "What is the difference between a 'Silent Change' and an announced change in production?",  # Comparison
        "Explain our monitoring setup and how to add new alerts"  # Multi-part
    ]
    
    for query in test_queries:
        print(f"\nOriginal: {query}")
        print(f"Should decompose: {decomposer.should_decompose(query)}")
        sub_queries = decomposer.decompose(query)
        print(f"Sub-queries: {sub_queries}")