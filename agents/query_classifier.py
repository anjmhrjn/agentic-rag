import json
import re
from llm.local_llm import LocalLLM

ALLOWED_DOC_TYPES = [
    "architecture", "concept", "database", "deployment",
    "disaster-recovery", "incident", "infrastructure", "networking",
    "observability", "onboarding", "performance", "postmortem",
    "process", "reference", "runbook", "security", "sop",
    "standard", "troubleshooting"
]

class QueryClassifierAgent:
    def __init__(self, model_path):
        self.llm = LocalLLM(model_path=model_path)

    def classify(self, query):
        allowed_types_str = ", ".join(ALLOWED_DOC_TYPES)
        prompt = open("prompts/query_classifier.txt").read().format(
            ALLOWED_DOC_TYPES=allowed_types_str,
            query=query
        )

        response = self.llm.generate(prompt)
        return self._extract_doc_types(response)

    def _extract_doc_types(self, response):
        """Robust JSON extraction with fallbacks"""
        # Try direct JSON parsing
        try:
            parsed = json.loads(response)
            doc_types = parsed.get("doc_types", [])
            # Validate against allowed types
            return [dt for dt in doc_types if dt in ALLOWED_DOC_TYPES][:4]
        except json.JSONDecodeError:
            pass
        
        # Try extracting JSON from text
        try:
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                parsed = json.loads(json_match.group(0))
                doc_types = parsed.get("doc_types", [])
                return [dt for dt in doc_types if dt in ALLOWED_DOC_TYPES][:4]
        except:
            pass
        
        # Last resort: extract any valid doc_types mentioned
        found_types = []
        for doc_type in ALLOWED_DOC_TYPES:
            if doc_type in response.lower():
                found_types.append(doc_type)
                if len(found_types) >= 4:
                    break
        
        return found_types if found_types else ["reference"]  # Default fallback