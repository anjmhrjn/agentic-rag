import logging
from agents.orchestrator import AdaptiveRAGOrchestrator
from agents.query_classifier import QueryClassifierAgent
from retriever.vector_retriever import VectorRetriever
from llm.local_llm import LocalLLM
from evaluation.benchmark import RAGBenchmark
from evaluation.compare import compare_configurations
from evaluation.test_dataset import get_test_subset

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_orchestrator(use_decomposition=True, use_reflection=True):
    """Factory function to create orchestrator with different configs"""
    llm = LocalLLM(model_path="models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf")
    classifier = QueryClassifierAgent(model_path="models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf")
    retriever = VectorRetriever(
        index_path="embeddings/faiss.index",
        meta_path="embeddings/chunk_meta.json"
    )
    
    return AdaptiveRAGOrchestrator(
        classifier=classifier,
        retriever=retriever,
        llm=llm,
        kb_size="small",
        use_decomposition=use_decomposition,
        use_reflection=use_reflection
    )

if __name__ == "__main__":
    print("Starting RAG System Evaluation\n")
    
    # Option 1: Quick single benchmark
    print("Running single configuration benchmark...")
    orchestrator = create_orchestrator(use_decomposition=False, use_reflection=False)
    benchmark = RAGBenchmark(orchestrator)
    test_dataset = get_test_subset(query_type="multi_part")
    aggregate = benchmark.run_benchmark(test_dataset)
    benchmark.print_summary(aggregate)
    
    # Option 2: Compare all configurations
    # print("Comparing all configurations...")
    # results = compare_configurations(create_orchestrator)
"""
## Expected Output
================================================================================
BENCHMARK SUMMARY
================================================================================

Total Queries: 11
Successful: 11
Error Rate: 0.0%

-------------------------------OVERALL METRICS----------------------------------
Overall Score:        0.847
Retrieval F1:         0.923
Retrieval Precision:  0.956
Retrieval Recall:     0.891
Citation Accuracy:    0.950
Topic Coverage:       0.812
Average Latency:      2.34s

---------------------------STRATEGY DISTRIBUTION--------------------------------
standard_rag        :   5 ( 45.5%)
complex_rag         :   3 ( 27.3%)
decomposed_rag      :   2 ( 18.2%)
lenient_rag         :   1 (  9.1%)

-------------------------------BY QUERY TYPE------------------------------------

SIMPLE:
  Count:        3
  Avg Score:    0.892
  Avg Latency:  1.23s

COMPLEX:
  Count:        3
  Avg Score:    0.834
  Avg Latency:  2.45s

MULTI_PART:
  Count:        3
  Avg Score:    0.856
  Avg Latency:  3.67s

OUT_OF_SCOPE:
  Count:        2
  Avg Score:    0.789
  Avg Latency:  1.12s

================================================================================
"""