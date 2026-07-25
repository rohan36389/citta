import logging
from typing import Dict, Any, List, Optional
from orchestration_context import OrchestrationContext
from knowledge_registry import get_registry

logger = logging.getLogger(__name__)

AMBIGUOUS_KEYWORDS = {
    "marketing": ["whatsapp_marketing", "influencer_marketing", "ai_powered_marketing"]
}

GENERIC_ENTITIES = {"company_info", "faq_general"}

class AmbiguityDetector:
    def __init__(self):
        self.reg = get_registry()

    def check_ambiguity(self, ctx: OrchestrationContext) -> OrchestrationContext:
        q_lower = ctx.normalized_query.lower().strip()
        words = q_lower.split()

        # If explicit specific entity is resolved (and not generic company_info), skip ambiguity
        if ctx.resolved_entity_id and ctx.resolved_entity_id not in GENERIC_ENTITIES:
            return ctx

        for kw, candidates in AMBIGUOUS_KEYWORDS.items():
            if q_lower == kw or q_lower == f"tell me about {kw}" or q_lower == f"what is {kw}" or q_lower == f"explain {kw}":
                ctx.is_ambiguous = True
                ctx.matched_entity_ids = candidates
                ctx.resolved_entity_id = None
                ctx.confidence = 0.7
                ctx.add_trace(
                    stage="AmbiguityDetector",
                    result=f"Ambiguity detected for keyword '{kw}' -> Candidates: {candidates}",
                    reason="Query matches multiple catalog entities"
                )
                return ctx

        return ctx

_ambiguity_detector_instance = None

def get_ambiguity_detector() -> AmbiguityDetector:
    global _ambiguity_detector_instance
    if _ambiguity_detector_instance is None:
        _ambiguity_detector_instance = AmbiguityDetector()
    return _ambiguity_detector_instance
