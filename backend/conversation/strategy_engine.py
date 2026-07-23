import logging
from typing import List
from backend.conversation.models import ConversationContext, IntentAnalysis, DiscoveryState, ResponseStrategy
from backend.conversation.interfaces import IStrategyEngine
from backend.conversation.config import OBJECTION_TEMPLATES

logger = logging.getLogger(__name__)

class StrategyEngine(IStrategyEngine):
    """
    Formulates conversation planning, applies pre-sales business policies,
    and maps objection handling procedures.
    """
    def __init__(self):
        pass

    def formulate_strategy(
        self,
        intent: IntentAnalysis,
        discovery: DiscoveryState,
        context: ConversationContext
    ) -> ResponseStrategy:
        """
        Adapts response strategy and parameters.
        """
        # Determine audience profile from company details
        if discovery.company_size == "Enterprise":
            audience = "CEO"
            length = "Detailed"
        else:
            audience = "General"
            length = "Medium"
            
        # Determine strategy from primary intent
        if intent.primary_intent == "pricing_inquiry":
            strat = "Objection"
            checklist = ["Handle commercial objections using custom quotes recommendation", "Suggest demo scheduling"]
            active_rules = ["Never guess custom pricing parameters"]
        elif intent.primary_intent == "technical_validation":
            strat = "Educational"
            audience = "Developer"
            checklist = ["Provide system components overview", "Recommend technical sandbox session"]
            active_rules = ["Ground technical integration capabilities check"]
        else:
            strat = "Consultative"
            checklist = ["Present solution benefits overview", "Qualify missing details: budget, timeline"]
            active_rules = ["Highlight client ROI metrics"]
            
        return ResponseStrategy(
            selected_strategy=strat,
            audience_level=audience,
            response_length=length,
            checklist=checklist,
            active_rules=active_rules
        )

    def plan_response(self, strategy: ResponseStrategy, context: ConversationContext) -> List[str]:
        """
        Generates action points and outline for composing response.
        """
        plan = []
        plan.append(f"Execute pre-sales strategy: {strategy.selected_strategy}")
        plan.extend(strategy.checklist)
        return plan

def get_strategy_engine() -> IStrategyEngine:
    return StrategyEngine()
