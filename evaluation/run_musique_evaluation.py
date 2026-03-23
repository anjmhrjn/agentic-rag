import json
from evaluation.benchmark import RAGBenchmark
from evaluation.test_dataset import TestQuery
from agents.orchestrator import AdaptiveRAGOrchestrator
from agents.query_classifier import QueryClassifierAgent
from retriever.vector_retriever import VectorRetriever
from llm.local_llm import LocalLLM

def load_musique_queries():
    """Load MusiQue test queries"""
    with open('evaluation/musique_test_dataset.json', encoding='utf-8') as f:
        data = json.load(f)
    
    test_queries = []
    for item in data:
        test_queries.append(TestQuery(
            query=item['query'],
            expected_sources=item['expected_sources'],
            expected_topics=item['expected_topics'],
            query_type=item['query_type'],
            difficulty=item['difficulty'],
            notes=item['notes']
        ))
    
    return test_queries

def run_musique_evaluation():
    """
    Run evaluation on MusiQue 3+ hop questions.
    
    This should be the BEST test for agentic benefits because:
    - Every question requires 3+ hops
    - Each hop needs different document
    - Decomposition is mandatory
    """
    
    test_queries = load_musique_queries()
    print(f"Loaded {len(test_queries)} MusiQue test queries (all 3+ hops)\n")
    
    # Initialize
    llm = LocalLLM(model_path="models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf")
    classifier = QueryClassifierAgent(model_path="models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf")
    retriever = VectorRetriever(
        index_path="embeddings/musique_faiss.index",
        meta_path="embeddings/musique_metadata.json"
    )
    
    configurations = [
        {
            "name": "Baseline (No Decomposition)",
            "kb_size": "medium",
            "use_decomposition": False,
            "use_reflection": False
        },
        {
            "name": "With Decomposition",
            "kb_size": "medium",
            "use_decomposition": True,
            "use_reflection": False
        },
        {
            "name": "Full Agentic (Decomp + Reflection)",
            "kb_size": "medium",
            "use_decomposition": True,
            "use_reflection": True
        }
    ]
    
    results = {}
    
    for config in configurations:
        print(f"\n{'='*80}")
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
    
    # Final comparison
    print("\n" + "="*80)
    print("MusiQue 3+ HOPS - ULTIMATE TEST FOR AGENTIC RAG")
    print("="*80)
    
    print(f"\n{'Configuration':<40} {'Score':<10} {'Recall':<10} {'MRR':<10} {'Latency':<10}")
    print("-" * 80)
    
    for name, metrics in results.items():
        print(f"{name:<40} "
              f"{metrics['avg_overall_score']:<10.3f} "
              f"{metrics['avg_critical_source_recall']:<10.3f} "
              f"{metrics['avg_mean_reciprocal_rank']:<10.3f} "
              f"{metrics['avg_latency']:<10.2f}s")
    
    # Analysis
    baseline = results["Baseline (No Decomposition)"]['avg_overall_score']
    decomp = results["With Decomposition"]['avg_overall_score']
    full = results["Full Agentic (Decomp + Reflection)"]['avg_overall_score']
    
    print("\n" + "="*80)
    print("IMPROVEMENT ANALYSIS")
    print("="*80)
    
    decomp_improvement = ((decomp - baseline) / baseline) * 100
    full_improvement = ((full - baseline) / baseline) * 100
    
    print(f"\nDecomposition improvement: {decomp_improvement:+.1f}%")
    print(f"Full Agentic improvement:  {full_improvement:+.1f}%")
    
    print(f"\n{'='*80}")
    print("VERDICT")
    print("="*80)
    
    if full_improvement >= 10:
        print("✅ SUCCESS! Agentic features show ≥10% improvement!")
        print("   3+ hop questions require decomposition.")
    elif full_improvement >= 5:
        print("⚠️ PARTIAL SUCCESS: 5-10% improvement")
        print("   Decomposition helps but not as much as expected.")
    else:
        print("❌ AGENTIC STILL DOESN'T HELP")
        print("\nPossible reasons:")
        print("  1. Retriever finds all docs in single top-10 retrieval")
        print("  2. 8B model loses information during synthesis")
        print("  3. Dataset may have answers in single paragraphs")
    
    return results

if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    run_musique_evaluation()