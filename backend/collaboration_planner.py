import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from agent_contracts import AgentID
from agent_planner import AgentPlan

logger = logging.getLogger(__name__)

class AgentExecutionStep(BaseModel):
    step_number: int
    agent_id: str
    dependencies: List[str] = Field(default_factory=list)
    allow_parallel: bool = True

class CollaborationGraph(BaseModel):
    graph_id: str
    task: str
    execution_steps: List[AgentExecutionStep] = Field(default_factory=list)

class CollaborationPlanner:
    def __init__(self):
        pass

    def build_collaboration_graph(self, plan: AgentPlan) -> CollaborationGraph:
        steps = []
        step_num = 1

        selected_ids = list(plan.selected_agent_ids)

        # Step 1: Memory Agent (if selected)
        if AgentID.MEMORY.value in selected_ids:
            steps.append(AgentExecutionStep(
                step_number=step_num,
                agent_id=AgentID.MEMORY.value,
                dependencies=[],
                allow_parallel=False
            ))
            step_num += 1
            selected_ids.remove(AgentID.MEMORY.value)

        # Step 2: Domain Agents (Research, Business, Technical, Workflow)
        domain_agents = [aid for aid in selected_ids if aid != AgentID.REVIEWER.value]
        memory_dep = [AgentID.MEMORY.value] if AgentID.MEMORY.value in plan.selected_agent_ids else []

        for aid in domain_agents:
            steps.append(AgentExecutionStep(
                step_number=step_num,
                agent_id=aid,
                dependencies=memory_dep,
                allow_parallel=True
            ))
            selected_ids.remove(aid)
        step_num += 1

        # Step 3: Reviewer Agent
        if AgentID.REVIEWER.value in plan.selected_agent_ids:
            steps.append(AgentExecutionStep(
                step_number=step_num,
                agent_id=AgentID.REVIEWER.value,
                dependencies=domain_agents,
                allow_parallel=False
            ))
            step_num += 1

        return CollaborationGraph(
            graph_id=f"graph_{int(step_num)}",
            task=plan.task,
            execution_steps=steps
        )

_collaboration_planner_instance = None

def get_collaboration_planner() -> CollaborationPlanner:
    global _collaboration_planner_instance
    if _collaboration_planner_instance is None:
        _collaboration_planner_instance = CollaborationPlanner()
    return _collaboration_planner_instance
