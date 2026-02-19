import logging
from typing import List, Dict, Set
import re

logger = logging.getLogger(__name__)

class RAGMetrics:
    """Calculate various metrics for RAG evaluation"""
    
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
    def retrieval_f1(retrieved_sources: List[str], 
                     expected_sources: List[str]) -> float:
        """
        Harmonic mean of precision and recall
        """
        precision = RAGMetrics.retrieval_precision(retrieved_sources, expected_sources)
        recall = RAGMetrics.retrieval_recall(retrieved_sources, expected_sources)
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)
    
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
    def calculate_all_metrics(
        query: str,
        answer: str,
        retrieved_sources: List[str],
        expected_sources: List[str],
        expected_topics: List[str],
        query_type: str,
        evaluation: Dict = None
    ) -> Dict:
        """Calculate all metrics for a single query result"""
        
        metrics = {
            # Retrieval metrics
            "retrieval_precision": RAGMetrics.retrieval_precision(retrieved_sources, expected_sources),
            "retrieval_recall": RAGMetrics.retrieval_recall(retrieved_sources, expected_sources),
            "retrieval_f1": RAGMetrics.retrieval_f1(retrieved_sources, expected_sources),
            
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
        
        # Calculate overall score (weighted average)
        weights = {
            "retrieval_f1": 0.3,
            "citation_accuracy": 0.2,
            "topic_coverage": 0.3,
            "answer_length_score": 0.1 if evaluation else 0.2,
            "quality_score": 0.1 if evaluation else 0.0
        }
        
        overall_score = sum(
            metrics.get(metric, 0) * weight 
            for metric, weight in weights.items()
            if metrics.get(metric) is not None
        )
        
        # Normalize if quality_score was not available
        if not evaluation:
            overall_score = overall_score / 0.9  # Redistribute the 0.1 weight
        
        metrics["overall_score"] = overall_score
        print(f"Metrics for query: {query}\n{metrics}\n")
        
        return metrics