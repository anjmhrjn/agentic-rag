# agents/query_decomposer.py

import json
import logging
from typing import List, Dict, Optional
from llm.local_llm import LocalLLM

class QueryDecomposerAgent:
    """
    Decomposes complex queries into simpler sub-queries.
    """
    
    def __init__(self, llm: LocalLLM):
        self.llm = llm
        self.logger = logging.getLogger(__name__)
    
    def should_decompose(self, query: str) -> bool:
        """
        Determine if query needs decomposition.
        """
        query_lower = query.lower()
        
        # Indicators of multi-part questions
        multi_part_indicators = [
            ' and ', ' or ', ' also ',
            'compare', 'difference between', 'versus', 'vs',
            'both', 'either',
            'as well as',
            'additionally',
            'furthermore'
        ]
        
        # Check for multiple questions
        has_multiple_questions = query.count('?') > 1
        
        # Check for multi-part indicators
        has_multi_part = any(indicator in query_lower for indicator in multi_part_indicators)
        
        # Check for multiple verbs (rough heuristic)
        action_words = ['how', 'what', 'why', 'when', 'where', 'explain', 'describe', 'show']
        action_count = sum(1 for word in action_words if word in query_lower)
        
        return has_multiple_questions or (has_multi_part and action_count >= 2)
    
    def decompose(self, query: str) -> List[str]:
        """
        Decompose query into sub-queries.
        Returns list of sub-queries, or [original_query] if no decomposition needed.
        """
        if not self.should_decompose(query):
            self.logger.info("Query doesn't need decomposition")
            return [query]
        
        self.logger.info(f"Decomposing query: {query}")
        
        prompt = self._build_decomposition_prompt(query)
        response = self.llm.generate(prompt)
        
        sub_queries = self._extract_sub_queries(response, query)
        
        self.logger.info(f"Decomposed into {len(sub_queries)} sub-queries: {sub_queries}")
        return sub_queries
    
    def _build_decomposition_prompt(self, query: str) -> str:
        """Build prompt for query decomposition"""
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You break complex questions into simpler sub-questions.

Rules:
- Break multi-part questions into 2-4 focused sub-questions
- Preserve all temporal context (durations, dates, timeframes)
- Each sub-question should be standalone and answerable independently
- Maintain the original intent and context
- Output ONLY valid JSON in this format: {{"sub_queries": ["question 1", "question 2"]}}

When decomposing:
- Ask yourself: "What decision is the user trying to make?"
- Don't add background questions unless the query is truly ambiguous
- Focus sub-queries on the SPECIFIC situation, not general concepts

Example:
Query: "Our API response time has doubled over the past 6 weeks. What should we do?"

BAD sub-queries:
- "What is an API?" (too basic)
- "How do APIs work?" (not tied to the problem)
- "How to build a REST API?" (wrong focus entirely)

GOOD sub-queries:
- "What common causes lead to sudden API latency increases?"
- "What monitoring data should be reviewed when response times spike?"
- "When should scaling infrastructure be considered versus optimizing code?"
<|eot_id|><|start_header_id|>user<|end_header_id|>

Question: "{query}"

Break this into 2-4 sub-questions. Output format:
{{"sub_queries": ["...", "..."]}}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        return prompt
    
    def _extract_sub_queries(self, response: str, original_query: str) -> List[str]:
        """Extract sub-queries from LLM response"""
        try:
            # Clean response
            cleaned = response.strip()
            if cleaned.startswith('```'):
                cleaned = cleaned.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            parsed = json.loads(cleaned)
            sub_queries = parsed.get("sub_queries", [])
            
            # Validate
            if not sub_queries or not isinstance(sub_queries, list):
                self.logger.warning("Invalid sub_queries format, using original query")
                return [original_query]
            
            # Filter out empty strings
            sub_queries = [q.strip() for q in sub_queries if q.strip()]
            
            # Limit to 4 sub-queries max
            if len(sub_queries) > 4:
                self.logger.warning(f"Too many sub-queries ({len(sub_queries)}), limiting to 4")
                sub_queries = sub_queries[:4]
            
            return sub_queries if sub_queries else [original_query]
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse decomposition response: {e}")
            return [original_query]
        except Exception as e:
            self.logger.error(f"Error extracting sub-queries: {e}")
            return [original_query]


# ==================== Usage Example ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    from llm.local_llm import LocalLLM
    
    llm = LocalLLM(model_path="models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf")
    decomposer = QueryDecomposerAgent(llm)
    
    test_queries = [
        "How do I restart a pod?",  # Simple - no decomposition
        "A feature flag has been enabled in production for 18 months. What should happen next and why?",  # Complex
        "You notice Redis memory at 76 percent during normal traffic. What actions should you take and why?",
        "What is the difference between a 'Silent Change' and an announced change in production?",  # Comparison
        "Explain our monitoring setup and how to add new alerts"  # Multi-part
    ]
    
    for query in test_queries:
        print(f"\nOriginal: {query}")
        print(f"Should decompose: {decomposer.should_decompose(query)}")
        sub_queries = decomposer.decompose(query)
        print(f"Sub-queries: {sub_queries}")