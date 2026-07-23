import logging
from typing import List
from backend.conversation.models import ConversationContext, IntentAnalysis, DiscoveryState, ResponseStrategy
from backend.conversation.interfaces import IStrategyEngine
from backend.conversation.config import OBJECTION_TEMPLATES

logger = logging.getLogger(__name__)

from backend.conversation.planning_engine import get_response_planning_engine

class StrategyEngine(IStrategyEngine):
    """
    Formulates conversation planning, applies pre-sales business policies,
    and maps objection handling procedures via ResponsePlanningEngine.
    """
    def __init__(self):
        self.planning_engine = get_response_planning_engine()

    def formulate_strategy(
        self,
        intent: IntentAnalysis,
        discovery: DiscoveryState,
        context: ConversationContext
    ) -> ResponseStrategy:
        """
        Adapts response strategy and parameters via ResponsePlanningEngine.
        """
        persona_profile = context.variables.get("persona_profile")
        response_plan = self.planning_engine.plan(intent, persona_profile, context)
        context.variables["response_plan"] = response_plan

        strat_name = response_plan.strategy_type.value
        checklist = [sec.title for sec in response_plan.sections]
        active_rules = [f"Maintain tone: {response_plan.tone}", f"CTA: {response_plan.cta}"]

        return ResponseStrategy(
            selected_strategy=strat_name,
            audience_level=response_plan.depth,
            response_length=response_plan.length,
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
