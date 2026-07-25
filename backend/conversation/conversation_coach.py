import logging
from typing import Dict, Any, List, Optional
from backend.conversation.behavior_policy import get_behavior_policy, BehaviorPolicy

logger = logging.getLogger(__name__)


class ConversationCoach:
    """
    Enterprise Conversation Coach.
    Acts as the internal enterprise conversation expert advising Planner, Composer, Suggestion Engine, and Validation Engine
    based on active BehaviorPolicy settings.
    """
    def __init__(self, policy: Optional[BehaviorPolicy] = None):
        self.policy = policy or get_behavior_policy()

    def recommend_strategy(self, intent_str: str, stage_str: str) -> str:
        """Recommends planning strategy blueprint based on intent and conversation stage."""
        p_intent = intent_str.lower()
        if "pricing" in p_intent or "cost" in p_intent:
            return "PRICING"
        elif "security" in p_intent or "compliance" in p_intent:
            return "SECURITY"
        elif "tech" in p_intent or "architecture" in p_intent or "integration" in p_intent:
            return "TECHNICAL"
        elif "recovery" in p_intent or "correction" in p_intent:
            return "RECOVERY"
        else:
            return "ENTERPRISE_CONSULTING"

    def guide_composition(self, raw_text: str, strategy: str) -> Dict[str, Any]:
        """Provides composition guidelines for progressive disclosure and length control."""
        return {
            "progressive_disclosure": self.policy.progressive_disclosure,
            "consultative_mode": self.policy.consultative_mode,
            "max_words": self.policy.max_words,
            "followup_required": self.policy.followup_required,
            "structure": self.policy.config.get("strategy_flow_blueprints", {}).get(strategy, [
                "Overview", "Business Value", "Capabilities", "Qualification", "Follow-up"
            ])
        }

    def get_validation_constraints(self) -> Dict[str, Any]:
        """Returns validation constraints for the ValidationEngine."""
        return {
            "pricing_guardrail": self.policy.pricing_guardrail,
            "max_words": self.policy.max_words,
            "auto_redirect": self.policy.auto_redirect
        }


_global_coach: Optional[ConversationCoach] = None

def get_conversation_coach() -> ConversationCoach:
    global _global_coach
    if _global_coach is None:
        _global_coach = ConversationCoach()
    return _global_coach
