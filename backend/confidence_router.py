import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfidenceLevel:
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    VERY_LOW = "VERY_LOW"

class ConfidenceRouter:
    def evaluate(
        self,
        confidence_score: float,
        is_deterministic: bool = False,
        has_exact_entity: bool = False
    ) -> Dict[str, Any]:
        if is_deterministic or has_exact_entity:
            return {
                "level": ConfidenceLevel.HIGH,
                "score": 1.0,
                "action": "DIRECT_ANSWER"
            }

        if confidence_score >= 0.70:
            return {
                "level": ConfidenceLevel.HIGH,
                "score": confidence_score,
                "action": "DIRECT_ANSWER"
            }
        elif confidence_score >= 0.50:
            return {
                "level": ConfidenceLevel.MEDIUM,
                "score": confidence_score,
                "action": "GROUNDED_ANSWER"
            }
        elif confidence_score >= 0.35:
            return {
                "level": ConfidenceLevel.LOW,
                "score": confidence_score,
                "action": "CLARIFICATION_QUESTION",
                "clarification_prompt": "Are you asking about our Enterprise OS solutions, our digital marketing platforms, or our AI strategy consulting services?"
            }
        else:
            return {
                "level": ConfidenceLevel.VERY_LOW,
                "score": confidence_score,
                "action": "POLITE_FALLBACK",
                "fallback_message": "I'm sorry, I don't currently have verified information about that in the CittaAI knowledge base. If you'd like, I can help you explore our available products, solutions, or services."
            }

_router_instance = None

def get_confidence_router() -> ConfidenceRouter:
    global _router_instance
    if _router_instance is None:
        _router_instance = ConfidenceRouter()
    return _router_instance
