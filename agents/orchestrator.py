import logging
from typing import List, Dict, Optional
from agents.query_classifier import QueryClassifierAgent
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
        kb_size: str = "small" # "small", "medium", "large"
    ):
        self.classifier = classifier
        self.retriever = retriever
        self.llm = llm
        self.logger = logging.getLogger(__name__)

        self.kb_size = kb_size
        self._set_thresholds()
    
    def _set_thresholds(self):
        """Set thresholds based on knowledge base size"""
        if self.kb_size == "small":  # < 500 docs
            self.HIGH_CONFIDENCE = 0.60  # Lowered from 0.75
            self.LOW_CONFIDENCE = 0.35   # Lowered from 0.5
            self.USE_DOC_TYPE_FILTER = False  # Disabled for small KB
            self.MIN_SIMILARITY = 0.4    # More lenient
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
        
        doc_types = None
        if use_classifier or self.USE_DOC_TYPE_FILTER:
            doc_types = self.classifier.classify(query)
            self.logger.info(f"Classified doc_types: {doc_types}")
        else:
            self.logger.info("Skipping doc_type filtering (small KB optimization)")
        
        relevance = self.retriever.get_relevance_score(query, top_k=5)
        self.logger.info(f"Relevance score: {relevance:.3f}")
        
        if relevance < self.LOW_CONFIDENCE:
            return self._handle_low_confidence(query, doc_types, relevance)
        
        if self._is_complex(query):
            return self._handle_complex_query(query, doc_types, relevance)
        
        return self._standard_rag(query, doc_types, relevance)
    
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
You are a DevOps expert assistant. Answer questions based on the provided documentation.
Be concise and cite sources using [DOC_ID] format.<|eot_id|><|start_header_id|>user<|end_header_id|>
Documentation:
{context}

Question: {query}

Answer the question based on the documentation above. Include relevant doc_ids in your answer.<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        return prompt
    
    def _build_complex_query_prompt(self, query: str, chunks: List[Dict]) -> str:
        """Build prompt for complex queries with chain-of-thought"""
        context = self._format_context(chunks)
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a DevOps expert assistant. For complex questions, break down your reasoning step by step.<|eot_id|><|start_header_id|>user<|end_header_id|>

Documentation:
{context}

Question: {query}

This is a complex question. Please:
1. Identify the key components of the question
2. Address each component using the documentation
3. Synthesize a comprehensive answer
4. Cite sources using [DOC_ID] format

Think through this step by step:<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        return prompt
    
#     def _build_low_confidence_prompt(self, query: str, chunks: List[Dict]) -> str:
#         """Build prompt when confidence is low"""
#         context = self._format_context(chunks)
        
#         prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
# You are a DevOps assistant. The available documentation may not fully answer this question.
# Be honest about limitations and clearly state what you're uncertain about.<|eot_id|><|start_header_id|>user<|end_header_id|>

# Available Documentation (may be incomplete):
# {context}

# Question: {query}

# Provide the best answer you can based on the documentation, but clearly state if the documentation doesn't fully cover the topic.<|eot_id|><|start_header_id|>assistant<|end_header_id|>

# """
#         return prompt
    
    def _build_no_context_prompt(self, query: str) -> str:
        """Build prompt when no context is available"""
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a DevOps assistant. No relevant documentation is available for this query.
Provide a general answer based on DevOps best practices, but clearly state this is not from the knowledge base.<|eot_id|><|start_header_id|>user<|end_header_id|>

Question: {query}

Note: No relevant documentation found in the knowledge base. Provide a general answer based on DevOps best practices.<|eot_id|><|start_header_id|>assistant<|end_header_id|>

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
        kb_size="small"
    )
    
    # Test queries
    test_queries = [
        "What is the specific command and flag required to scale the RDS cluster immediately during a high-traffic event?",
        "Why is PostgreSQL used for billing and order data instead of a NoSQL solution like DynamoDB?",
        "Explain the difference between blue-green and canary deployments, and when to use each",
        "What is the best way to cook pasta?"
    ]

    print("\n" + "="*80)
    print("Testing WITHOUT doc_type filtering")
    print("="*80)
    
    for query in test_queries:
        print("\n" + "="*80)
        print(f"Query: {query}")
        print("="*80)
        
        result = orchestrator.process_query(query, use_classifier=False)
        
        print(f"\nStrategy: {result['strategy']}")
        print(f"Confidence: {result['confidence']:.3f}")
        if 'warning' in result:
            print(f"Warning: {result['warning']}")
        if 'info' in result:
            print(f"Info: {result['info']}")
        print(f"\nAnswer:\n{result['answer']}")
        print(f"\nSources: {result['sources']}")
    
    print("\n" + "="*80)
    print("Testing WITH doc_type filtering (optional)")
    print("="*80)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = orchestrator.process_query(query, use_classifier=True)
        
        print(f"Strategy: {result['strategy']}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Sources: {result['sources']}")
        print(f"Answer: {result['answer'][:200]}...")