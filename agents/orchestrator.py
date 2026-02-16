import logging
from typing import List, Dict, Optional
from agents.query_classifier import QueryClassifierAgent
from agents.query_decomposer import QueryDecomposerAgent
from retriever.vector_retriever import VectorRetriever
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
    ):
        self.classifier = classifier
        self.retriever = retriever
        self.llm = llm
        self.logger = logging.getLogger(__name__)

        self.use_decomposition = use_decomposition
        if use_decomposition:
            self.decomposer = QueryDecomposerAgent(llm)

        self.kb_size = kb_size
        self._set_thresholds()
    
    def _set_thresholds(self):
        """Set thresholds based on knowledge base size"""
        if self.kb_size == "small":  # < 500 docs
            self.HIGH_CONFIDENCE = 0.60 
            self.LOW_CONFIDENCE = 0.35
            self.USE_DOC_TYPE_FILTER = False  # Disabled for small KB
            self.MIN_SIMILARITY = 0.4
            self.DEFAULT_TOP_K = 5
            
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

        for i, sub_query in enumerate(sub_queries, 1):
            self.logger.info(f"Processing sub-query {i}/{len(sub_queries)}: {sub_query}")
            
            # Get doc types for this sub-query
            doc_types = None
            if use_classifier or self.USE_DOC_TYPE_FILTER:
                doc_types = self.classifier.classify(sub_query)
            
            # Retrieve context for sub-query
            context_chunks = self.retriever.retrieve(
                sub_query,
                top_k=self.DEFAULT_TOP_K,
                doc_type_filter=doc_types,
                similarity_threshold=self.MIN_SIMILARITY
            )
            
            if context_chunks:
                # Generate answer for sub-query
                prompt = self._build_sub_query_prompt(sub_query, context_chunks)
                answer = self.llm.generate(prompt)
                
                sub_results.append({
                    "sub_query": sub_query,
                    "answer": answer,
                    "sources": [c.get("doc_id", "unknown") for c in context_chunks]
                })
                
                # Collect all sources
                for chunk in context_chunks:
                    doc_id = chunk.get("doc_id", "unknown")
                    if doc_id not in all_sources:
                        all_sources.append(doc_id)
        
        # Synthesize final answer
        final_answer = self._synthesize_answers(query, sub_results)
        
        return {
            "answer": final_answer,
            "sources": all_sources,
            "strategy": "decomposed_rag",
            "confidence": 0.8,  # High confidence for decomposed queries
            "info": f"Answered via {len(sub_queries)} sub-queries",
            "sub_results": sub_results  # Include for debugging
        }
    
    def _build_sub_query_prompt(self, sub_query: str, chunks: List[Dict]) -> str:
        """Build prompt for answering a sub-query"""
        context = self._format_context(chunks)
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a DevOps expert. Answer this specific sub-question concisely based on documentation.
Output ONLY valid JSON: {{"answer": "concise answer with [DOC_ID] citations"}}
<|eot_id|><|start_header_id|>user<|end_header_id|>

Documentation:
{context}

Sub-question: {sub_query}

Provide a focused answer. Output format:
{{"answer": "..."}}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        return prompt
    
    def _synthesize_answers(self, original_query: str, sub_results: List[Dict]) -> str:
        """
        Synthesize sub-answers into a comprehensive final answer.
        """
        # Build synthesis prompt
        sub_answers_text = "\n\n".join([
            f"Q: {sr['sub_query']}\nA: {sr['answer']}"
            for sr in sub_results
        ])
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a DevOps expert. Synthesize multiple sub-answers into one comprehensive answer.
Combine information logically, maintain citations, avoid repetition.
Output ONLY valid JSON: {{"answer": "comprehensive synthesized answer"}}
<|eot_id|><|start_header_id|>user<|end_header_id|>

Original Question: {original_query}

Sub-answers to synthesize:
{sub_answers_text}

Synthesize these into one comprehensive answer to the original question.
Maintain all [DOC_ID] citations. Output format:
{{"answer": "..."}}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        answer = self.llm.generate(prompt)
        return answer

    
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

        if doc_types and self.USE_DOC_TYPE_FILTER:
            context_chunks = self.retriever.retrieve(
                query,
                top_k=self.DEFAULT_TOP_K + 2,
                doc_type_filter=doc_types,
                similarity_threshold=self.MIN_SIMILARITY
            )
            
            # If filtering yields too few results, retry without filter
            if len(context_chunks) < 3:
                self.logger.warning(f"Doc_type filter too restrictive ({len(context_chunks)} results), retrying without filter")
                context_chunks = self.retriever.retrieve(
                    query,
                    top_k=self.DEFAULT_TOP_K + 2,
                    doc_type_filter=None,
                    similarity_threshold=self.MIN_SIMILARITY
                )
        else:
            # Small KB: No filtering
            context_chunks = self.retriever.retrieve(
                query,
                top_k=self.DEFAULT_TOP_K + 2,
                doc_type_filter=None,
                similarity_threshold=self.MIN_SIMILARITY
            )
        
        if not context_chunks:
            return self._handle_low_confidence(query, doc_types, relevance)
        
        # Use chain-of-thought prompting for complex reasoning
        prompt = self._build_complex_query_prompt(query, context_chunks)
        answer = self.llm.generate(prompt)
        sources = [c.get("doc_id", "unknown") for c in context_chunks]
        
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
        
        # Standard retrieval
        if doc_types and self.USE_DOC_TYPE_FILTER:
            context_chunks = self.retriever.retrieve(
                query,
                top_k=self.DEFAULT_TOP_K,
                doc_type_filter=doc_types,
                similarity_threshold=self.MIN_SIMILARITY
            )
            
            # Fallback: If filtered results are too few, remove filter
            if len(context_chunks) < 2:
                self.logger.warning(f"Doc_type filter yielded only {len(context_chunks)} results, retrying without filter")
                context_chunks = self.retriever.retrieve(
                    query,
                    top_k=self.DEFAULT_TOP_K,
                    doc_type_filter=None,
                    similarity_threshold=self.MIN_SIMILARITY
                )
        else:
            # Small KB or classifier disabled: no filtering
            context_chunks = self.retriever.retrieve(
                query,
                top_k=self.DEFAULT_TOP_K,
                doc_type_filter=None,
                similarity_threshold=self.MIN_SIMILARITY
            )
        
        if not context_chunks:
            return self._handle_low_confidence(query, doc_types, relevance)
        
        # Generate answer
        prompt = self._build_standard_prompt(query, context_chunks)
        answer = self.llm.generate(prompt)
        sources = [c.get("doc_id", "unknown") for c in context_chunks]
        
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
        use_decomposition=True
    )

    # ============= Testing query with query decomposition =============
    query = "A feature flag has been enabled in production for 18 months. What should happen next and why?"
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")

    result = orchestrator.process_query(query, use_classifier=True)

    print(f"Strategy: {result['strategy']}")
    print(f"Confidence: {result['confidence']:.3f}")
    print(f"Info: {result.get('info', 'N/A')}")
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nSources: {result['sources']}")

    if 'sub_results' in result:
        print(f"\n{'='*80}")
        print("Sub-query breakdown:")
        print(f"{'='*80}")
        for i, sr in enumerate(result['sub_results'], 1):
            print(f"\n{i}. {sr['sub_query']}")
            print(f"   Answer: {sr['answer']}")
            print(f"   Sources: {sr['sources']}")

    

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