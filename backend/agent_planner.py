import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from orchestration_context import OrchestrationContext
from agent_contracts import AgentID

logger = logging.getLogger(__name__)

class AgentPlan(BaseModel):
    task: str
    selected_agent_ids: List[str] = Field(default_factory=list)
    reasoning: str = ""

class AgentPlanner:
    def __init__(self):
        pass

    def plan_agents(self, ctx: OrchestrationContext) -> AgentPlan:
        q_lower = ctx.normalized_query.lower().strip()
        selected = []
        reasons = []

        # Memory Agent check
        if any(w in q_lower for w in ["continue", "last week", "previous", "history", "yesterday"]):
            selected.append(AgentID.MEMORY.value)
            reasons.append("Historical context/memory restoration required.")

        # Business Solutions Agent check
        if any(w in q_lower for w in ["recommend", "best", "hospital", "university", "business", "value", "roi", "suitable"]):
            selected.append(AgentID.BUSINESS_SOLUTIONS.value)
            reasons.append("Business suitability & value evaluation required.")

        # Research Agent check
        if any(w in q_lower for w in ["compare", "vs", "versus", "difference", "research", "specs"]):
            selected.append(AgentID.RESEARCH.value)
            reasons.append("Product comparison & catalog research required.")

        # Technical Architecture Agent check
        if any(w in q_lower for w in ["architecture", "integrate", "integration", "tech", "deploy", "deployment", "implementation"]):
            selected.append(AgentID.TECHNICAL_ARCHITECTURE.value)
            reasons.append("Technical architecture & integration mapping required.")

        # Workflow Agent check
        if any(w in q_lower for w in ["schedule", "demo", "ticket", "action", "workflow", "roadmap"]):
            selected.append(AgentID.WORKFLOW.value)
            reasons.append("Workflow action sequence planning required.")

        # Default fallback selection if none matched
        if not selected:
            selected = [AgentID.BUSINESS_SOLUTIONS.value, AgentID.TECHNICAL_ARCHITECTURE.value]

        # Reviewer Agent is ALWAYS attached
        if AgentID.REVIEWER.value not in selected:
            selected.append(AgentID.REVIEWER.value)

        # Deduplicate
        selected = list(dict.fromkeys(selected))

        return AgentPlan(
            task=ctx.original_query,
            selected_agent_ids=selected,
            reasoning="; ".join(reasons) if reasons else "Multi-agent collaboration planned."
        )

_agent_planner_instance = None

def get_agent_planner() -> AgentPlanner:
    global _agent_planner_instance
    if _agent_planner_instance is None:
        _agent_planner_instance = AgentPlanner()
    return _agent_planner_instance
