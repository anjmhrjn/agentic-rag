import logging
from evaluation.benchmark import RAGBenchmark
from evaluation.test_dataset import get_test_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compare_configurations(orchestrator_factory):
    """
    Compare different configurations of the RAG system.
    
    Args:
        orchestrator_factory: Function that creates orchestrator with given config
    """
    
    test_dataset = get_test_dataset()
    
    configurations = [
        {
            "name": "Baseline (no decomposition, no reflection)",
            "use_decomposition": False,
            "use_reflection": False
        },
        {
            "name": "With Decomposition Only",
            "use_decomposition": True,
            "use_reflection": False
        },
        {
            "name": "With Reflection Only",
            "use_decomposition": False,
            "use_reflection": True
        },
        {
            "name": "Full Agentic (decomposition + reflection)",
            "use_decomposition": True,
            "use_reflection": True
        }
    ]
    
    results = {}
    
    for config in configurations:
        print("\n" + "="*80)
        print(f"TESTING: {config['name']}")
        print("="*80)
        
        # Create orchestrator with this configuration
        orchestrator = orchestrator_factory(
            use_decomposition=config['use_decomposition'],
            use_reflection=config['use_reflection']
        )
        
        # Run benchmark
        benchmark = RAGBenchmark(orchestrator)
        aggregate = benchmark.run_benchmark(test_dataset, save_results=True)
        
        # Store results
        results[config['name']] = aggregate
        
        # Print summary
        benchmark.print_summary(aggregate)
    
    # Print comparison
    print("\n" + "="*80)
    print("CONFIGURATION COMPARISON")
    print("="*80)
    
    print(f"\n{'Configuration':<50} {'Score':<10} {'F1':<10} {'Latency':<10}")
    print("-" * 80)
    
    for name, metrics in results.items():
        print(f"{name:<50} "
              f"{metrics['avg_overall_score']:<10.3f} "
              f"{metrics['avg_retrieval_f1']:<10.3f} "
              f"{metrics['avg_latency']:<10.2f}s")
    
    return results