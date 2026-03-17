# run_medium_kb_evaluation.py

import json
from evaluation.benchmark import RAGBenchmark
from evaluation.test_dataset import TestQuery

def load_hotpotqa_test_queries():
    """Load HotpotQA test queries"""
    with open('evaluation/hotpotqa_test_dataset.json') as f:
        data = json.load(f)
    
    test_queries = []
    for item in data:
        test_queries.append(TestQuery(
            query=item['query'],
            expected_sources=item['expected_sources'],
            expected_topics=item['expected_topics'],
            query_type=item['query_type'],
            difficulty=item['difficulty'],
            notes=item.get('notes', '')
        ))
    
    return test_queries

def compare_small_vs_medium_kb():
    """Compare agentic features on medium KB vs small KB"""
    
    from agents.orchestrator import AdaptiveRAGOrchestrator
    from agents.query_classifier import QueryClassifierAgent
    from retriever.vector_retriever import VectorRetriever
    from llm.local_llm import LocalLLM
    
    # Load test queries
    test_queries = load_hotpotqa_test_queries()
    print(f"Loaded {len(test_queries)} test queries")
    
    # Initialize components
    llm = LocalLLM(model_path="models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf")
    classifier = QueryClassifierAgent(model_path="models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf")
    retriever = VectorRetriever(
        index_path="embeddings/hotpotqa_faiss.index",
        meta_path="embeddings/hotpotqa_metadata.json"
    )
    
    configurations = [
        {
            "name": "Medium KB - No Features",
            "kb_size": "medium",
            "use_decomposition": False,
            "use_reflection": False
        },
        {
            "name": "Medium KB - With Decomposition",
            "kb_size": "medium",
            "use_decomposition": True,
            "use_reflection": False
        },
        {
            "name": "Medium KB - Full Agentic",
            "kb_size": "medium",
            "use_decomposition": True,
            "use_reflection": True
        }
    ]
    
    results = {}
    
    for config in configurations:
        print("\n" + "="*80)
        print(f"Testing: {config['name']}")
        print("="*80)
        
        orchestrator = AdaptiveRAGOrchestrator(
            classifier=classifier,
            retriever=retriever,
            llm=llm,
            kb_size=config['kb_size'],
            use_decomposition=config['use_decomposition'],
            use_reflection=config['use_reflection']
        )
        
        benchmark = RAGBenchmark(orchestrator)
        aggregate = benchmark.run_benchmark(test_queries, save_results=True)
        
        results[config['name']] = aggregate
        benchmark.print_summary(aggregate)
    
    # Print comparison
    print("\n" + "="*80)
    print("MEDIUM KB COMPARISON")
    print("="*80)
    
    print(f"\n{'Configuration':<35} {'Score':<10} {'MRR':<10} {'Latency':<10}")
    print("-" * 70)
    
    for name, metrics in results.items():
        print(f"{name:<35} "
              f"{metrics['avg_overall_score']:<10.3f} "
              f"{metrics['avg_mean_reciprocal_rank']:<10.3f} "
              f"{metrics['avg_latency']:<10.2f}s")
    
    return results

if __name__ == "__main__":
    compare_small_vs_medium_kb()