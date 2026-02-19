import logging
from typing import List, Dict, Optional
from agents.query_classifier import QueryClassifierAgent
from agents.query_decomposer import QueryDecomposerAgent
from agents.answer_evaluator import AnswerEvaluator
from retriever.vector_retriever import VectorRetriever
import numpy as np
from llm.local_llm import LocalLLM

class AdaptiveRAGOrchestrator:
    """
    Main orchestrator for adaptive RAG system.
    Routes queries based on complexity and confidence.
    Less aggressive filtering, more forgiving thresholds.
    """
    
    def __init__(
        self, 
        classifier: QueryClassifierAgent,
        retriever: VectorRetriever,
        llm: LocalLLM,
        kb_size: str = "small", # "small", "medium", "large"
        use_decomposition: bool = True,
        use_reflection: bool = True,
    ):
        self.classifier = classifier
        self.retriever = retriever
        self.llm = llm
        self.logger = logging.getLogger(__name__)

        self.use_decomposition = use_decomposition
        if use_decomposition:
            self.decomposer = QueryDecomposerAgent(llm)

        self.use_reflection = use_reflection
        if use_reflection:
            self.evaluator = AnswerEvaluator(llm)

        self.kb_size = kb_size
        self._set_thresholds()

        self.MAX_RETRIES = 2 if self.use_reflection else 1
    
    def _set_thresholds(self):
        """Set thresholds based on knowledge base size"""
        if self.kb_size == "small":  # < 500 docs
            self.HIGH_CONFIDENCE = 0.60 
            self.LOW_CONFIDENCE = 0.35
            self.USE_DOC_TYPE_FILTER = False  # Disabled for small KB
            self.MIN_SIMILARITY = 0.4
            self.DEFAULT_TOP_K = 3
            
        elif self.kb_size == "medium":  # 500-5000 docs
            self.HIGH_CONFIDENCE = 0.70
            self.LOW_CONFIDENCE = 0.45
            self.USE_DOC_TYPE_FILTER = True
            self.MIN_SIMILARITY = 0.6
            self.DEFAULT_TOP_K = 7
            
        else:  # large: > 5000 docs
            self.HIGH_CONFIDENCE = 0.75
            self.LOW_CONFIDENCE = 0.5
            self.USE_DOC_TYPE_FILTER = True
            self.MIN_SIMILARITY = 0.7
            self.DEFAULT_TOP_K = 10
        
        self.logger.info(f"KB size: {self.kb_size}, thresholds adjusted")
    
    def process_query(self, query: str, use_classifier: bool = False) -> Dict:
        """
        Main entry point - processes query through adaptive pipeline.
        
        Returns:
            Dict with 'answer', 'sources', 'strategy', 'confidence'
        """
        self.logger.info(f"Processing query: {query}")

        if use_classifier and not self.USE_DOC_TYPE_FILTER:
            self.USE_DOC_TYPE_FILTER = True  # Enable filtering if classifier is used:

        if self.use_decomposition and self.decomposer.should_decompose(query):
            return self._process_decomposed_query(query, use_classifier)
        
        doc_types = None
        if use_classifier or self.USE_DOC_TYPE_FILTER:
            doc_types = self.classifier.classify(query)
            self.logger.info(f"Classified doc_types: {doc_types}")
        else:
            self.logger.info("Skipping doc_type filtering (small KB optimization)")
        
        relevance = self.retriever.get_relevance_score(query, top_k=self.DEFAULT_TOP_K)
        self.logger.info(f"Relevance score: {relevance:.3f}")
        
        if relevance < self.LOW_CONFIDENCE:
            return self._handle_low_confidence(query, doc_types, relevance)
        
        if self._is_complex(query):
            return self._handle_complex_query(query, doc_types, relevance)
        
        return self._standard_rag(query, doc_types, relevance)
    
    def _process_decomposed_query(self, query: str, use_classifier: bool) -> Dict:
        """
        Process query by decomposing into sub-queries.
        Retrieve and answer each sub-query, then synthesize final answer.
        """

        sub_queries = self.decomposer.decompose(query)

        if len(sub_queries) == 1:
            # Decomposition determined not needed after all
            return self.process_query(query, use_classifier)
        
        sub_results = []
        all_sources = []
        relevance = []
        all_context_chunks = []

        for i, sub_query in enumerate(sub_queries, 1):
            self.logger.info(f"Processing sub-query {i}/{len(sub_queries)}: {sub_query}")
            
            # Get doc types for this sub-query
            doc_types = None
            if use_classifier or self.USE_DOC_TYPE_FILTER:
                doc_types = self.classifier.classify(sub_query)
            
            sub_result = self._process_sub_query_with_reflection(sub_query, doc_types)

            if sub_result:
                sub_results.append(sub_result)
                relevance.append(sub_result.get("relevance", 0.0))
                all_context_chunks.extend(sub_result.get("chunks", []))

                for source in sub_result['sources']:
                    if source not in all_sources:
                        all_sources.append(source)
        if not sub_results:
            self.logger.warning("No valid sub-results, falling back")
            return self._handle_low_confidence(query, None, 0.3)
        
        confidence = np.mean(relevance) if len(relevance) > 0 else 0.0
        final_result = self._synthesize_with_reflection(query, sub_results, all_sources, all_context_chunks, confidence)

        return final_result
    
    def _process_sub_query_with_reflection(self, sub_query: str, doc_types: Optional[List[str]]) -> Optional[Dict]:
        attempt = 0
        best_result = None

        # Retrieve context for sub-query
        context_chunks = self.retriever.retrieve(
            sub_query,
            top_k=self.DEFAULT_TOP_K,
            doc_type_filter=doc_types,
            similarity_threshold=self.MIN_SIMILARITY
        )

        while attempt < self.MAX_RETRIES:
            attempt += 1
            self.logger.info(f"Sub-query generation attempt {attempt}/{self.MAX_RETRIES}")
            
            if context_chunks:
                # Generate answer for sub-query
                prompt = self._build_sub_query_prompt(sub_query, context_chunks)
                answer = self.llm.generate(prompt)
                sources = [c.get("doc_id", "unknown") for c in context_chunks]

                sim_score = []
                for chunk in context_chunks:
                    sim_score.append(chunk.get("similarity_score", 0.0))
                relevance = np.mean(sim_score) if len(sim_score) > 0 else 0.0

                if self.use_reflection:
                    evaluation = self.evaluator.evaluate(sub_query, answer, sources, context_chunks)
                    
                    self.logger.info(f"Sub-query quality: {evaluation['quality_score']:.3f}")

                    current_result = {
                        "sub_query": sub_query,
                        "answer": answer,
                        "sources": sources,
                        "evaluation": evaluation,
                        "attempts": attempt,
                        "relevance": relevance,
                        "chunks": context_chunks,
                    }
                    
                    if not evaluation['needs_regeneration']:
                        return current_result
                    
                    if best_result is None or evaluation['quality_score'] > best_result['evaluation']['quality_score']:
                        best_result = current_result
                    
                    self.logger.warning(f"Sub-query answer quality poor ({evaluation['quality_score']:.3f}), issues: {evaluation['issues']}")

                    if attempt < self.MAX_RETRIES:
                        context_chunks = self.retriever.retrieve(
                            sub_query,
                            top_k=self.DEFAULT_TOP_K + 3,
                            doc_type_filter=doc_types,
                            similarity_threshold=max(self.MIN_SIMILARITY - 0.1, 0.3)
                        )
                else:
                    return {
                        "sub_query": sub_query,
                        "answer": answer,
                        "sources": sources,
                        "attempts": attempt,
                        "relevance": relevance,
                        "chunks": context_chunks,
                    }
        
        if best_result:
            best_result["warning"] = "Sub-query answer quality below threshold"
            return best_result
        return None
                
        
        # Synthesize final answer
        # final_answer = self._synthesize_answers(query, sub_results)
        
        # return {
        #     "answer": final_answer,
        #     "sources": all_sources,
        #     "strategy": "decomposed_rag",
        #     "confidence": np.mean(relevance) if len(relevance) > 0 else 0.0,
        #     "info": f"Answered via {len(sub_queries)} sub-queries",
        #     "sub_results": sub_results  # Include for debugging
        # }
    
    def _build_sub_query_prompt(self, sub_query: str, chunks: List[Dict]) -> str:
        """Build prompt for answering a sub-query"""
        context = self._format_context(chunks)
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a DevOps expert. Answer this specific sub-question concisely based on documentation.
Output ONLY valid JSON: {{"answer": "concise answer with [DOC_ID] citations"}}
Include relevant citations in the format [DOC_ID] where appropriate.
<|eot_id|><|start_header_id|>user<|end_header_id|>

Documentation:
{context}

Sub-question: {sub_query}

Provide a focused answer. Output format:
{{"answer": "..."}}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        return prompt
    
    def _synthesize_with_reflection(
        self, 
        original_query: str, 
        sub_results: List[Dict], 
        all_sources: List[str], 
        all_context_chunks: List[Dict],
        confidence: float
    ) -> str:
        """
        Synthesize sub-answers into a comprehensive final answer.
        """
        attempt = 0
        best_synthesis = None

        # Build synthesis prompt
        sub_answers_text = "\n\n".join([
            f"Q: {sr['sub_query']}\nA: {sr['answer']}"
            for sr in sub_results
        ])
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a DevOps expert. Synthesize multiple sub-answers into one comprehensive answer.
Combine information logically, maintain all citations, avoid repetition.
Output ONLY valid JSON: {{"answer": "comprehensive synthesized answer"}}
<|eot_id|><|start_header_id|>user<|end_header_id|>

Rules:
- Only cite doc_ids that appear in the sub-answers. The citations should be in the format [DOC_ID].
- Ensure answer directly addresses the original question
- Base all claims on the provided sub-answers
- Combine information logically without repetition

Original Question: {original_query}

Sub-answers to synthesize:
{sub_answers_text}

Synthesize these into one comprehensive answer to the original question.
Maintain all [DOC_ID] citations. Output format:
{{"answer": "..."}}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        while attempt < self.MAX_RETRIES:
            attempt += 1
            self.logger.info(f"Synthesis attempt {attempt}/{self.MAX_RETRIES}")

            answer = self.llm.generate(prompt)

            if self.use_reflection:
                seen_ids = set()
                unique_chunks = []
                for chunk in all_context_chunks:
                    doc_id = chunk.get("doc_id", "")
                    if doc_id and doc_id not in seen_ids:
                        seen_ids.add(doc_id)
                        unique_chunks.append(chunk)

                evaluation = self.evaluator.evaluate(original_query, answer, all_sources, unique_chunks)

                self.logger.info(f"Synthesis quality: {evaluation['quality_score']:.3f}")
            
                current_synthesis = {
                    "answer": answer,
                    "sources": all_sources,
                    "strategy": "decomposed_rag",
                    "confidence": confidence,
                    "info": f"Answered via {len(sub_results)} sub-queries",
                    "sub_results": sub_results,
                    "evaluation": evaluation,
                    "synthesis_attempts": attempt
                }

                # If synthesis quality is acceptable, return
                if not evaluation['needs_regeneration']:
                    self.logger.info("Synthesis quality acceptable")
                    return current_synthesis
                
                # Store best synthesis
                if best_synthesis is None or evaluation['quality_score'] > best_synthesis['evaluation']['quality_score']:
                    best_synthesis = current_synthesis
                
                # Quality is poor - modify synthesis prompt for retry
                self.logger.warning(f"Synthesis quality poor ({evaluation['quality_score']:.3f}), retrying...")
                
                if attempt < self.MAX_RETRIES:
                    # Add guidance based on issues
                    issues_text = "; ".join(evaluation['issues'])
                    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a DevOps expert. Synthesize multiple sub-answers into one comprehensive answer.

IMPORTANT: Previous synthesis had issues: {issues_text}
Address these issues in your synthesis.

Rules:
- Only cite doc_ids that appear in the sub-answers. The citations should be in the format [DOC_ID].
- Ensure answer directly addresses the original question
- Base all claims on the provided sub-answers
- Combine information logically without repetition

Output ONLY valid JSON: {{"answer": "comprehensive synthesized answer"}}
<|eot_id|><|start_header_id|>user<|end_header_id|>

Original Question: {original_query}

Sub-answers to synthesize:
{sub_answers_text}

Synthesize carefully, addressing the issues mentioned. Output format:
{{"answer": "..."}}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
            else:
                # No reflection - return immediately
                return {
                    "answer": answer,
                    "sources": all_sources,
                    "strategy": "decomposed_rag",
                    "confidence": confidence,
                    "info": f"Answered via {len(sub_results)} sub-queries",
                    "sub_results": sub_results,
                    "synthesis_attempts": attempt
                }

        self.logger.warning("Max synthesis retries reached, using best attempt")
        if best_synthesis:
            best_synthesis['warning'] = "Synthesis quality below threshold after retries"
            return best_synthesis
        
        # Fallback
        return {
            "answer": "Synthesis attempt failed to produce a high-quality answer.",
            "sources": all_sources,
            "strategy": "decomposed_rag",
            "confidence": confidence,
            "info": f"Answered via {len(sub_results)} sub-queries",
            "sub_results": sub_results,
            "warning": "Quality checks failed"
        }

    
    def _handle_low_confidence(
        self, 
        query: str, 
        doc_types: Optional[List[str]],
        relevance: float
    ) -> Dict:
        """
        Handle queries where KB has low relevance.
        Strategy: Use LLM's general knowledge + warn user.
        """
        self.logger.warning(f"Low confidence ({relevance:.3f}) - Using LLM fallback")
        
        # Try to retrieve anyway (might have some useful context)
        context_chunks = self.retriever.retrieve(
            query,
            top_k=3,
            doc_type_filter=None,
            similarity_threshold=0.0  # Lower threshold
        )
        
        if context_chunks:
            # Generate with limited context + disclaimer
            prompt = self._build_standard_prompt(query, context_chunks)
            answer = self.llm.generate(prompt)
            sources = [c.get("doc_id", "unknown") for c in context_chunks]
            
            return {
                "answer": answer,
                "sources": sources,
                "strategy": "low_confidence_rag",
                "confidence": relevance,
                "warning": "Low confidence - answer may not be fully accurate"
            }
        else:
            # No relevant context - pure LLM
            prompt = self._build_no_context_prompt(query)
            answer = self.llm.generate(prompt)
            
            return {
                "answer": answer,
                "sources": [],
                "strategy": "llm_only",
                "confidence": 0.0,
                "warning": "No relevant documentation found - using general knowledge"
            }
    
    def _handle_complex_query(
        self, 
        query: str, 
        doc_types: Optional[List[str]],
        relevance: float
    ) -> Dict:
        """
        Handle complex queries requiring multiple retrieval steps.
        Strategy: Retrieve more context, use chain-of-thought.
        """
        self.logger.info(f"Complex query detected - using enhanced retrieval")

        context_chunks = self.retriever.retrieve(
            query,
            top_k=self.DEFAULT_TOP_K + 1,
            doc_type_filter=doc_types,
            similarity_threshold=self.MIN_SIMILARITY
        )
        
        if not context_chunks:
            return self._handle_low_confidence(query, doc_types, relevance)

        attempt = 0
        while attempt < self.MAX_RETRIES:
            attempt += 1
            self.logger.info(f"Generation attempt {attempt}/{self.MAX_RETRIES}")

            prompt = self._build_complex_query_prompt(query, context_chunks)
            answer = self.llm.generate(prompt)
            sources = [c.get("doc_id", "unknown") for c in context_chunks]
            
            if self.use_reflection:
                evaluation = self.evaluator.evaluate(query, answer, sources, context_chunks)
                
                if not evaluation['needs_regeneration']:
                    return {
                        "answer": answer,
                        "sources": sources,
                        "strategy": "complex_rag",
                        "confidence": relevance,
                        "info": f"Retrieved {len(context_chunks)} relevant chunks",
                        "evaluation": evaluation,
                        "generation_attempts": attempt
                    }
                
                if attempt < self.MAX_RETRIES:
                    # Retry with even more context
                    context_chunks = self.retriever.retrieve(
                        query,
                        top_k=self.DEFAULT_TOP_K + 3,
                        doc_type_filter=None,
                        similarity_threshold=max(self.MIN_SIMILARITY - 0.15, 0.2)
                    )
            else:
                return {
                    "answer": answer,
                    "sources": sources,
                    "strategy": "complex_rag",
                    "confidence": relevance,
                    "info": f"Retrieved {len(context_chunks)} relevant chunks"
                }
        
        return {
            "answer": answer,
            "sources": sources,
            "strategy": "complex_rag",
            "confidence": relevance,
            "info": f"Retrieved {len(context_chunks)} relevant chunks"
        }
    
    def _standard_rag(
        self, 
        query: str, 
        doc_types: Optional[List[str]],
        relevance: float
    ) -> Dict:
        """
        Standard RAG pipeline for simple, high-confidence queries.
        Strategy: Retrieve top-k, generate concise answer.
        """
        self.logger.info(f"Standard RAG - High confidence ({relevance:.3f})")
        
        context_chunks = self.retriever.retrieve(
            query,
            top_k=self.DEFAULT_TOP_K,
            doc_type_filter=doc_types,
            similarity_threshold=self.MIN_SIMILARITY
        )
        
        if not context_chunks:
            return self._handle_low_confidence(query, doc_types, relevance)
        
        attempt = 0
        best_result = None

        while attempt < self.MAX_RETRIES:
            attempt += 1
            self.logger.info(f"Generation attempt {attempt}/{self.MAX_RETRIES}")
        
            # Generate answer
            prompt = self._build_standard_prompt(query, context_chunks)
            answer = self.llm.generate(prompt)
            sources = [c.get("doc_id", "unknown") for c in context_chunks]

            if self.use_reflection:
                evaluation = self.evaluator.evaluate(query, answer, sources, context_chunks)
                
                self.logger.info(f"Quality score: {evaluation['quality_score']:.3f}")
                
                # If quality is good enough, return
                if not evaluation['needs_regeneration']:
                    self.logger.info("Answer quality acceptable, returning")
                    return {
                        "answer": answer,
                        "sources": sources,
                        "strategy": "standard_rag",
                        "confidence": relevance,
                        "evaluation": evaluation,
                        "generation_attempts": attempt
                    }
                
                # Store best attempt so far
                if best_result is None or evaluation['quality_score'] > best_result['evaluation']['quality_score']:
                    best_result = {
                        "answer": answer,
                        "sources": sources,
                        "strategy": "standard_rag",
                        "confidence": relevance,
                        "evaluation": evaluation,
                        "generation_attempts": attempt
                    }
                
                # Quality is poor - try regeneration with more context
                self.logger.warning(f"Quality poor ({evaluation['quality_score']:.3f}), issues: {evaluation['issues']}")
                
                if attempt < self.MAX_RETRIES:
                    self.logger.info("Retrieving more context for retry...")
                    # Retrieve more context for retry
                    context_chunks = self.retriever.retrieve(
                        query,
                        top_k=self.DEFAULT_TOP_K + 3,
                        doc_type_filter=doc_types,
                        similarity_threshold=max(self.MIN_SIMILARITY - 0.1, 0.3)
                    )
            else:
                # No reflection - return immediately
                return {
                    "answer": answer,
                    "sources": sources,
                    "strategy": "standard_rag",
                    "confidence": relevance
                }
        
        self.logger.warning(f"Max retries reached, returning best attempt")
        if best_result:
            best_result["warning"] = "Answer quality below threshold after retries"
            return best_result
        
        return {
            "answer": answer,
            "sources": sources,
            "strategy": "standard_rag",
            "confidence": relevance
        }
    
    def _is_complex(self, query: str) -> bool:
        """
        Determine if query is complex based on keywords and structure.
        """
        query_lower = query.lower()

        # Complex indicators
        complex_keywords = [
            "how to", "what are", "explain", "compare", 
            "difference between", "differences", "steps to", "process for",
            "why", "when should"
        ]
        
        # Check for complex keywords
        has_complex_keyword = any(
            keyword in query_lower 
            for keyword in complex_keywords
        )
        has_multiple_questions = query.count('?') > 1
        has_conjunctions = ' and ' in query_lower or ' or ' in query_lower
        is_long = len(query.split()) > 20
        
        return (
            has_complex_keyword or 
            has_multiple_questions or 
            has_conjunctions or 
            is_long
        )
    
    def _build_standard_prompt(self, query: str, chunks: List[Dict]) -> str:
        """Build prompt for standard RAG"""
        context = self._format_context(chunks)
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a DevOps expert. Answer questions based on documentation.
Output ONLY valid JSON in this EXACT format:
{{"answer": "your detailed answer here with [DOC_ID] citations"}}

Do NOT include "type", "id", "question", or any other fields.
Do NOT repeat the question.
Include relevant citations in the format [DOC_ID] where appropriate.
Only output the JSON object with the "answer" field.<|eot_id|><|start_header_id|>user<|end_header_id|>

Documentation:
{context}

Question: {query}

Output format:
{{"answer": "..."}}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        return prompt
    
    def _build_complex_query_prompt(self, query: str, chunks: List[Dict]) -> str:
        """Build prompt for complex queries with chain-of-thought"""
        context = self._format_context(chunks)
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a DevOps expert. For complex questions, provide comprehensive answers.
Output ONLY valid JSON in this EXACT format:
{{"answer": "your detailed answer with [DOC_ID] citations"}}

Do NOT include "type", "id", "question", or any other fields.
Include relevant citations in the format [DOC_ID] where appropriate.
Only output the JSON object with the "answer" field.<|eot_id|><|start_header_id|>user<|end_header_id|>

Documentation:
{context}

Question: {query}

Provide a comprehensive answer. Output format:
{{"answer": "..."}}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        return prompt
    
    def _build_no_context_prompt(self, query: str) -> str:
        """Build prompt when no context is available"""
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a DevOps assistant. No documentation is available.
Provide general DevOps knowledge.
Output ONLY valid JSON in this EXACT format:
{{"answer": "your general answer based on best practices"}}

Do NOT include "type", "id", "question", or any other fields.
Only output the JSON object with the "answer" field.<|eot_id|><|start_header_id|>user<|end_header_id|>

Question: {query}

Note: No relevant documentation found. Provide general answer.
Output format:
{{"answer": "..."}}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        return prompt
    
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

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize components
    from agents.query_classifier import QueryClassifierAgent
    from retriever.vector_retriever import VectorRetriever
    from llm.local_llm import LocalLLM
    
    classifier = QueryClassifierAgent(
        model_path="models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
    )
    
    retriever = VectorRetriever(
        index_path="embeddings/faiss.index",
        meta_path="embeddings/chunk_meta.json"
    )
    
    llm = LocalLLM(
        model_path="models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
    )
    
    # Create orchestrator
    orchestrator = AdaptiveRAGOrchestrator(
        classifier=classifier,
        retriever=retriever,
        llm=llm,
        kb_size="small",
        use_decomposition=True,
        use_reflection=False
    )

    query = "A feature flag has been enabled in production for 18 months. What should happen next and why?"
    # query = "During a deployment, the canary shows a 0.1 percent increase in errors. Should you proceed? What factors matter?"
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")

    result = orchestrator.process_query(query, use_classifier=True)

    print(f"Strategy: {result['strategy']}")
    print(f"Confidence: {result['confidence']:.3f}")
    print(f"Info: {result.get('info', 'N/A')}")
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nSources: {result['sources']}")

    if 'evaluation' in result:
        eval_data = result['evaluation']
        print(f"\n📊 Quality Evaluation:")
        print(f"  Overall Quality: {eval_data['quality_score']:.3f}")
        print(f"  Citation Score: {eval_data['citation_score']:.3f}")
        print(f"  Relevance Score: {eval_data['relevance_score']:.3f}")
        print(f"  Support Score: {eval_data['support_score']:.3f}")
        print(f"  Generation Attempts: {result.get('generation_attempts', 1)}")
        
        if eval_data['issues']:
            print(f"Issues: {eval_data['issues']}")
        
        print(f"  Recommendation: {eval_data['recommendation']}")

    # if 'sub_results' in result:
    #     print(f"\n{'='*80}")
    #     print("Sub-query breakdown:")
    #     print(f"{'='*80}")
    #     for i, sr in enumerate(result['sub_results'], 1):
    #         print(f"\n{i}. {sr['sub_query']}")
    #         print(f"   Answer: {sr['answer']}")
    #         print(f"   Sources: {sr['sources']}")

    

    # ============= Testing muliple queries with and without doc_type filtering =============
    # Test queries
    # test_queries = [
    #     # "What is the specific command and flag required to scale the RDS cluster immediately during a high-traffic event?",
    #     "Why is PostgreSQL used for billing and order data instead of a NoSQL solution like DynamoDB?",
    #     # "Explain the difference between blue-green and canary deployments, and when to use each",
    #     # "What is the best way to cook pasta?"
    # ]

    # print("\n" + "="*80)
    # print("Testing WITHOUT doc_type filtering")
    # print("="*80)
    
    # for query in test_queries:
    #     print("\n" + "="*80)
    #     print(f"Query: {query}")
    #     print("="*80)
        
    #     result = orchestrator.process_query(query, use_classifier=False)
        
    #     print(f"\nStrategy: {result['strategy']}")
    #     print(f"Confidence: {result['confidence']:.3f}")
    #     if 'warning' in result:
    #         print(f"Warning: {result['warning']}")
    #     if 'info' in result:
    #         print(f"Info: {result['info']}")
    #     print(f"\nAnswer:\n{result['answer']}")
    #     print(f"\nSources: {result['sources']}")
    
    # print("\n" + "="*80)
    # print("Testing WITH doc_type filtering (optional)")
    # print("="*80)
    
    # for query in test_queries:
    #     print(f"\nQuery: {query}")
    #     result = orchestrator.process_query(query, use_classifier=True)
        
    #     print(f"Strategy: {result['strategy']}")
    #     print(f"Confidence: {result['confidence']:.3f}")
    #     print(f"Sources: {result['sources']}")
    #     print(f"Answer: {result['answer']}")