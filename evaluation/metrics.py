import logging
from typing import List, Dict, Set
import re

logger = logging.getLogger(__name__)

class RAGMetrics:
    """Improved metrics for RAG evaluation"""

    @staticmethod
    def retrieval_precision(retrieved_sources: List[str], 
                           expected_sources: List[str]) -> float:
        """
        What percentage of retrieved docs are relevant?
        Precision = (relevant retrieved) / (total retrieved)
        """
        if not retrieved_sources:
            return 0.0
        
        retrieved_set = set(retrieved_sources)
        expected_set = set(expected_sources)
        
        relevant_retrieved = retrieved_set.intersection(expected_set)
        
        return len(relevant_retrieved) / len(retrieved_set)
    
    @staticmethod
    def retrieval_recall(retrieved_sources: List[str], 
                        expected_sources: List[str]) -> float:
        """
        What percentage of relevant docs were retrieved?
        Recall = (relevant retrieved) / (total relevant)
        """
        if not expected_sources:
            return 1.0  # No expected sources = perfect recall
        
        retrieved_set = set(retrieved_sources)
        expected_set = set(expected_sources)
        
        relevant_retrieved = retrieved_set.intersection(expected_set)
        
        return len(relevant_retrieved) / len(expected_set)
    
    @staticmethod
    def citation_accuracy(answer: str, retrieved_sources: List[str]) -> float:
        """
        Are all citations in the answer valid?
        Returns: percentage of citations that exist in retrieved sources
        """
        # Extract citations from answer
        cited_docs = re.findall(r'\[([A-Z]+-\d+)\]', answer)
        
        if not cited_docs:
            # No citations - could be good or bad depending on answer length
            if len(answer) < 50:
                return 1.0  # Short answer doesn't need citations
            return 0.5  # Long answer without citations is suspicious
        
        valid_sources = set(retrieved_sources)
        valid_citations = sum(1 for doc in cited_docs if doc in valid_sources)
        
        return valid_citations / len(cited_docs)
    
    @staticmethod
    def topic_coverage(answer: str, expected_topics: List[str]) -> float:
        """
        What percentage of expected topics are covered in the answer?
        """
        if not expected_topics:
            return 1.0
        
        answer_lower = answer.lower()
        topics_covered = sum(1 for topic in expected_topics if topic.lower() in answer_lower)
        
        return topics_covered / len(expected_topics)
    
    @staticmethod
    def answer_length_score(answer: str, query_type: str) -> float:
        """
        Is the answer appropriately sized for the query type?
        """
        word_count = len(answer.split())
        
        expected_ranges = {
            "simple": (20, 150),
            "complex": (50, 300),
            "multi_part": (100, 500),
            "out_of_scope": (10, 100)
        }
        
        min_words, max_words = expected_ranges.get(query_type, (20, 200))
        
        if word_count < min_words:
            return word_count / min_words  # Too short
        elif word_count > max_words:
            return max_words / word_count  # Too long
        else:
            return 1.0  # Just right
    
    @staticmethod
    def critical_source_recall(retrieved_sources: List[str], 
                               expected_sources: List[str]) -> float:
        """
        Did we retrieve the critical/expected sources?
        This is what really matters for RAG.
        
        Returns: 1.0 if ALL expected sources retrieved, 0.0-1.0 otherwise
        """
        if not expected_sources:
            return 1.0
        
        retrieved_set = set(retrieved_sources)
        expected_set = set(expected_sources)
        
        critical_retrieved = retrieved_set.intersection(expected_set)
        
        # Percentage of critical sources we found
        return len(critical_retrieved) / len(expected_set)
    
    @staticmethod
    def mean_reciprocal_rank(retrieved_sources: List[str], 
                            expected_sources: List[str]) -> float:
        """
        What position was the first relevant document?
        1.0 if rank 1, 0.5 if rank 2, 0.33 if rank 3, etc.
        
        This measures: "How quickly did we find a relevant doc?"
        """
        if not expected_sources:
            return 1.0
        
        expected_set = set(expected_sources)
        
        for rank, source in enumerate(retrieved_sources, start=1):
            if source in expected_set:
                return 1.0 / rank
        
        return 0.0  # No relevant docs found
    
    @staticmethod
    def retrieval_success_at_k(retrieved_sources: List[str],
                               expected_sources: List[str],
                               k: int = 3) -> float:
        """
        Did we retrieve at least one expected source in top-k?
        
        This is a binary metric: 1.0 if yes, 0.0 if no.
        More forgiving than precision for RAG use cases.
        """
        if not expected_sources:
            return 1.0
        
        top_k = set(retrieved_sources[:k])
        expected_set = set(expected_sources)
        
        return 1.0 if top_k.intersection(expected_set) else 0.0
    
    @staticmethod
    def rank_of_best_source(retrieved_sources: List[str],
                           expected_sources: List[str]) -> int:
        """
        What rank (1-indexed) is the first expected source?
        Lower is better. Returns -1 if not found.
        """
        if not expected_sources:
            return 1
        
        expected_set = set(expected_sources)
        
        for rank, source in enumerate(retrieved_sources, start=1):
            if source in expected_set:
                return rank
        
        return -1  # Not found
    
    @staticmethod
    def retrieval_precision_at_k(retrieved_sources: List[str],
                                 expected_sources: List[str],
                                 k: int = 3) -> float:
        """
        Precision but only for top-k results.
        More fair for RAG where we always retrieve 5 but only use top 3.
        """
        if not retrieved_sources:
            return 0.0
        
        top_k = retrieved_sources[:k]
        retrieved_set = set(top_k)
        expected_set = set(expected_sources)
        
        relevant_retrieved = retrieved_set.intersection(expected_set)
        
        return len(relevant_retrieved) / len(top_k)
    
    @staticmethod
    def calculate_all_metrics(
        query: str,
        answer: str,
        retrieved_sources: List[str],
        expected_sources: List[str],
        expected_topics: List[str],
        query_type: str,
        evaluation: Dict = None
    ) -> Dict:
        """Calculate all metrics - UPDATED for RAG"""
        
        metrics = {
            "critical_source_recall": RAGMetrics.critical_source_recall(
                retrieved_sources, expected_sources
            ),
            "mean_reciprocal_rank": RAGMetrics.mean_reciprocal_rank(
                retrieved_sources, expected_sources
            ),
            "success_at_3": RAGMetrics.retrieval_success_at_k(
                retrieved_sources, expected_sources, k=3
            ),
            "success_at_5": RAGMetrics.retrieval_success_at_k(
                retrieved_sources, expected_sources, k=5
            ),
            "rank_of_best": RAGMetrics.rank_of_best_source(
                retrieved_sources, expected_sources
            ),
            "precision_at_3": RAGMetrics.retrieval_precision_at_k(
                retrieved_sources, expected_sources, k=3
            ),
            
            # For comparison only - not part of overall score
            "retrieval_precision_full": RAGMetrics.retrieval_precision(
                retrieved_sources, expected_sources
            ),
            "retrieval_recall": RAGMetrics.retrieval_recall(
                retrieved_sources, expected_sources
            ),
            
            # Answer quality metrics
            "citation_accuracy": RAGMetrics.citation_accuracy(answer, retrieved_sources),
            "topic_coverage": RAGMetrics.topic_coverage(answer, expected_topics),
            "answer_length_score": RAGMetrics.answer_length_score(answer, query_type),
            
            # Evaluation metrics (if reflection was used)
            "quality_score": evaluation.get("quality_score") if evaluation else None,
            "citation_score": evaluation.get("citation_score") if evaluation else None,
            "relevance_score": evaluation.get("relevance_score") if evaluation else None,
            "support_score": evaluation.get("support_score") if evaluation else None,
        }

        weights = {
            "critical_source_recall": 0.30,                         # Did we get the important docs?
            "mean_reciprocal_rank": 0.10,                           # How quickly?
            "citation_accuracy": 0.20,                              # Valid citations?
            "topic_coverage": 0.20,                                 # Right topics?
            "answer_length_score": 0.10 if evaluation else 0.20,    # Appropriate length?
            "quality_score": 0.10 if evaluation else 0.0            # LLM quality check
        }
        
        overall_score = sum(
            metrics.get(metric, 0) * weight 
            for metric, weight in weights.items()
            if metrics.get(metric) is not None
        )
        
        # Normalize if quality_score wasn't available
        if not evaluation:
            overall_score = overall_score / 0.9
        
        metrics["overall_score"] = overall_score
        
        return metrics