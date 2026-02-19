import logging
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import json
from datetime import datetime

from evaluation.test_dataset import TestQuery, get_test_dataset
from evaluation.metrics import RAGMetrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BenchmarkResult:
    """Results for a single test query"""
    query: str
    answer: str
    sources: List[str]
    strategy: str
    confidence: float
    latency: float
    metrics: Dict
    evaluation: Optional[Dict] = None
    error: Optional[str] = None

class RAGBenchmark:
    """Benchmark RAG system performance"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.results: List[BenchmarkResult] = []
    
    def run_benchmark(
        self, 
        test_dataset: List[TestQuery] = None,
        use_classifier: bool = False,
        save_results: bool = True
    ) -> Dict:
        """
        Run benchmark on test dataset.
        Returns aggregate metrics.
        """
        if test_dataset is None:
            test_dataset = get_test_dataset()
        
        logger.info(f"Starting benchmark with {len(test_dataset)} test queries")
        logger.info(f"Configuration: use_classifier={use_classifier}")
        
        self.results = []
        
        for i, test_query in enumerate(test_dataset, 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"Test {i}/{len(test_dataset)}: {test_query.query}")
            logger.info(f"Type: {test_query.query_type}, Difficulty: {test_query.difficulty}")
            
            try:
                # Run query and measure latency
                start_time = time.time()
                result = self.orchestrator.process_query(
                    test_query.query,
                    use_classifier=use_classifier
                )
                latency = time.time() - start_time
                
                # Calculate metrics
                metrics = RAGMetrics.calculate_all_metrics(
                    query=test_query.query,
                    answer=result['answer'],
                    retrieved_sources=result['sources'],
                    expected_sources=test_query.expected_sources,
                    expected_topics=test_query.expected_topics,
                    query_type=test_query.query_type,
                    evaluation=result.get('evaluation')
                )
                
                # Store result
                benchmark_result = BenchmarkResult(
                    query=test_query.query,
                    answer=result['answer'],
                    sources=result['sources'],
                    strategy=result['strategy'],
                    confidence=result['confidence'],
                    latency=latency,
                    metrics=metrics,
                    evaluation=result.get('evaluation')
                )
                
                self.results.append(benchmark_result)
                
                # Log key metrics
                logger.info(f"Strategy: {result['strategy']}")
                logger.info(f"Latency: {latency:.2f}s")
                logger.info(f"Overall Score: {metrics['overall_score']:.3f}")
                logger.info(f"Retrieval F1: {metrics['retrieval_f1']:.3f}")
                logger.info(f"Topic Coverage: {metrics['topic_coverage']:.3f}")
                
            except Exception as e:
                logger.error(f"Error processing query: {e}")
                self.results.append(BenchmarkResult(
                    query=test_query.query,
                    answer="",
                    sources=[],
                    strategy="error",
                    confidence=0.0,
                    latency=0.0,
                    metrics={},
                    error=str(e)
                ))
        
        # Calculate aggregate metrics
        aggregate = self._calculate_aggregate_metrics()
        
        # Save results
        if save_results:
            self._save_results(aggregate, use_classifier)
        
        return aggregate
    
    def _calculate_aggregate_metrics(self) -> Dict:
        """Calculate aggregate metrics across all test queries"""
        
        # Filter out errors
        valid_results = [r for r in self.results if not r.error]
        
        if not valid_results:
            return {"error": "No valid results"}
        
        # Aggregate by query type
        by_type = {}
        for result in valid_results:
            # Determine query type from test dataset
            test_query = next(
                (q for q in get_test_dataset() if q.query == result.query),
                None
            )
            if test_query:
                qtype = test_query.query_type
                if qtype not in by_type:
                    by_type[qtype] = []
                by_type[qtype].append(result)
        
        # Overall metrics
        overall = {
            "total_queries": len(self.results),
            "successful_queries": len(valid_results),
            "error_rate": (len(self.results) - len(valid_results)) / len(self.results),
            
            # Average metrics
            "avg_overall_score": self._avg([r.metrics.get('overall_score', 0) for r in valid_results]),
            "avg_retrieval_f1": self._avg([r.metrics.get('retrieval_f1', 0) for r in valid_results]),
            "avg_retrieval_precision": self._avg([r.metrics.get('retrieval_precision', 0) for r in valid_results]),
            "avg_retrieval_recall": self._avg([r.metrics.get('retrieval_recall', 0) for r in valid_results]),
            "avg_citation_accuracy": self._avg([r.metrics.get('citation_accuracy', 0) for r in valid_results]),
            "avg_topic_coverage": self._avg([r.metrics.get('topic_coverage', 0) for r in valid_results]),
            "avg_latency": self._avg([r.latency for r in valid_results]),
            
            # Strategy breakdown
            "strategy_distribution": self._strategy_distribution(valid_results),
            
            # By query type
            "by_query_type": {
                qtype: {
                    "count": len(results),
                    "avg_score": self._avg([r.metrics.get('overall_score', 0) for r in results]),
                    "avg_latency": self._avg([r.latency for r in results])
                }
                for qtype, results in by_type.items()
            }
        }
        
        return overall
    
    def _avg(self, values: List[float]) -> float:
        """Calculate average, handling empty lists"""
        return sum(values) / len(values) if values else 0.0
    
    def _strategy_distribution(self, results: List[BenchmarkResult]) -> Dict:
        """Count how often each strategy was used"""
        distribution = {}
        for result in results:
            strategy = result.strategy
            distribution[strategy] = distribution.get(strategy, 0) + 1
        return distribution
    
    def _save_results(self, aggregate: Dict, use_classifier: bool):
        """Save benchmark results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_str = "with_classifier" if use_classifier else "no_classifier"
        filename = f"evaluation/results/benchmark_{timestamp}_{config_str}.json"
        
        output = {
            "timestamp": timestamp,
            "configuration": {
                "use_classifier": use_classifier,
                "use_decomposition": self.orchestrator.use_decomposition,
                "use_reflection": self.orchestrator.use_reflection,
                "kb_size": self.orchestrator.kb_size
            },
            "aggregate_metrics": aggregate,
            "individual_results": [asdict(r) for r in self.results]
        }
        
        import os
        os.makedirs("evaluation/results", exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"\nResults saved to: {filename}")
    
    def print_summary(self, aggregate: Dict):
        """Print formatted summary of results"""
        print("\n" + "="*80)
        print("BENCHMARK SUMMARY")
        print("="*80)
        
        print(f"\nTotal Queries: {aggregate['total_queries']}")
        print(f"Successful: {aggregate['successful_queries']}")
        print(f"Error Rate: {aggregate['error_rate']:.1%}")
        
        print(f"\n{'OVERALL METRICS':-^80}")
        print(f"Overall Score:        {aggregate['avg_overall_score']:.3f}")
        print(f"Retrieval F1:         {aggregate['avg_retrieval_f1']:.3f}")
        print(f"Retrieval Precision:  {aggregate['avg_retrieval_precision']:.3f}")
        print(f"Retrieval Recall:     {aggregate['avg_retrieval_recall']:.3f}")
        print(f"Citation Accuracy:    {aggregate['avg_citation_accuracy']:.3f}")
        print(f"Topic Coverage:       {aggregate['avg_topic_coverage']:.3f}")
        print(f"Average Latency:      {aggregate['avg_latency']:.2f}s")
        
        print(f"\n{'STRATEGY DISTRIBUTION':-^80}")
        for strategy, count in aggregate['strategy_distribution'].items():
            percentage = (count / aggregate['successful_queries']) * 100
            print(f"{strategy:20s}: {count:3d} ({percentage:5.1f}%)")
        
        print(f"\n{'BY QUERY TYPE':-^80}")
        for qtype, stats in aggregate['by_query_type'].items():
            print(f"\n{qtype.upper()}:")
            print(f"  Count:        {stats['count']}")
            print(f"  Avg Score:    {stats['avg_score']:.3f}")
            print(f"  Avg Latency:  {stats['avg_latency']:.2f}s")
        
        print("\n" + "="*80)