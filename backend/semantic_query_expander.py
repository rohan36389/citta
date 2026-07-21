import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

CONCEPT_EXPANSION_MAP: Dict[str, List[str]] = {
    "ecommerce": ["online shopping", "digital commerce", "marketplace", "retail store", "online store"],
    "e-commerce": ["online shopping", "digital commerce", "marketplace", "retail store"],
    "healthcare": ["hospital", "medical", "pharma", "clinic", "patient care", "health tech"],
    "pharma": ["pharmaceutical", "healthcare", "drug discovery", "clinical trials", "medical OS"],
    "education": ["schools", "universities", "LMS", "learning platform", "edtech", "academic"],
    "real estate": ["property", "housing", "realty", "construction", "commercial real estate"],
    "ai": ["Artificial Intelligence", "Machine Learning", "Deep Learning", "Generative AI", "LLM", "Agentic AI", "GraphRAG"],
    "ml": ["Machine Learning", "Artificial Intelligence", "Deep Learning", "Predictive Modeling"],
    "llm": ["Large Language Model", "Generative AI", "AI Model", "Foundation Model"],
    "rag": ["Retrieval-Augmented Generation", "Vector Search", "Knowledge Base Retrieval"],
    "smart cities": ["urban planning", "iot", "infrastructure", "traffic management", "civic tech"],
    "martech": ["marketing technology", "analytics", "campaign management", "customer data platform"]
}

class SemanticQueryExpander:
    def expand(self, query: str) -> str:
        q_lower = query.lower().strip()
        expansions: List[str] = []

        for concept, terms in CONCEPT_EXPANSION_MAP.items():
            pattern = rf"\b{re.escape(concept)}\b"
            if re.search(pattern, q_lower):
                expansions.extend(terms[:2])

        if expansions:
            # Deduplicate while preserving order
            unique_exp = list(dict.fromkeys(expansions))
            expanded_str = query + " (" + ", ".join(unique_exp) + ")"
            logger.info(f"Query expanded: '{query}' -> '{expanded_str}'")
            return expanded_str

        return query

_expander_instance = None

def get_semantic_query_expander() -> SemanticQueryExpander:
    global _expander_instance
    if _expander_instance is None:
        _expander_instance = SemanticQueryExpander()
    return _expander_instance

