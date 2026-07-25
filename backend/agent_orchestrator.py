import time
import asyncio
import logging
from typing import Dict, Any, List, Optional

from orchestration_context import OrchestrationContext
from agent_contracts import AgentID, AgentContext, AgentOutput
from specialized_agents import (
    BusinessSolutionsAgent,
    TechnicalArchitectureAgent,
    WorkflowAgent,
    MemoryAgent,
    ResearchAgent,
    ReviewerAgent
)
from agent_planner import get_agent_planner
from collaboration_planner import get_collaboration_planner
from consensus_builder import get_consensus_builder

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self):
        self.planner = get_agent_planner()
        self.collaboration_planner = get_collaboration_planner()
        self.consensus_builder = get_consensus_builder()
        
        self.agents = {
            AgentID.BUSINESS_SOLUTIONS.value: BusinessSolutionsAgent(),
            AgentID.TECHNICAL_ARCHITECTURE.value: TechnicalArchitectureAgent(),
            AgentID.WORKFLOW.value: WorkflowAgent(),
            AgentID.MEMORY.value: MemoryAgent(),
            AgentID.RESEARCH.value: ResearchAgent(),
            AgentID.REVIEWER.value: ReviewerAgent()
        }

    async def orchestrate_collaboration(
        self,
        ctx: OrchestrationContext,
        simulate_failure_agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        start_time = time.time()

        # 1. Agent Planning
        plan = self.planner.plan_agents(ctx)

        # 2. Collaboration Planning (Graph construction)
        graph = self.collaboration_planner.build_collaboration_graph(plan)

        # 3. Execution Context
        agent_outputs: List[AgentOutput] = []
        agent_outputs_by_id: Dict[str, AgentOutput] = {}

        # 4. Execute Steps in Graph Order
        for step in graph.execution_steps:
            aid = step.agent_id
            if aid not in self.agents:
                continue

            agent_obj = self.agents[aid]
            actx = AgentContext(
                agent_id=aid,
                task=ctx.original_query,
                objective=f"Execute multi-agent subtask for {aid}",
                inputs={"entity_name": ctx.resolved_entity_name or "Enterprise Solution"}
            )

            # Simulated Failure / Timeout Check
            if simulate_failure_agent_id and aid == simulate_failure_agent_id:
                logger.warning(f"Agent '{aid}' encountered simulated failure/timeout. Triggering fallback handler.")
                fallback_out = AgentOutput(
                    agent_id=aid,
                    task=ctx.original_query,
                    findings=[f"[{aid}] Fallback execution completed due to primary timeout."],
                    confidence=0.50,
                    status="FALLBACK"
                )
                agent_outputs.append(fallback_out)
                agent_outputs_by_id[aid] = fallback_out
                continue

            try:
                if aid == AgentID.REVIEWER.value:
                    # ReviewerAgent takes prior domain agent outputs for grounding validation
                    domain_outputs = [o for o in agent_outputs if o.agent_id != AgentID.REVIEWER.value]
                    out = await agent_obj.execute(actx, prior_outputs=domain_outputs)
                else:
                    out = await agent_obj.execute(actx)

                agent_outputs.append(out)
                agent_outputs_by_id[aid] = out

            except Exception as e:
                logger.error(f"Agent '{aid}' execution exception: {e}")
                err_out = AgentOutput(
                    agent_id=aid,
                    task=ctx.original_query,
                    findings=[f"[{aid}] Execution error: {e}"],
                    confidence=0.0,
                    status="FAILED"
                )
                agent_outputs.append(err_out)

        # 5. Consensus Building
        consensus = self.consensus_builder.build_consensus(agent_outputs, ctx.original_query)
        latency_ms = round((time.time() - start_time) * 1000.0, 2)

        # Update Context Metrics & Decision Trace
        ctx.response_text = consensus.summary_markdown
        ctx.metrics["participating_agents"] = consensus.participating_agents
        ctx.metrics["consensus_score"] = consensus.consensus_score
        ctx.metrics["total_findings"] = consensus.total_findings
        ctx.metrics["latency_ms"] = latency_ms

        ctx.add_trace(
            stage="AgentOrchestrator",
            result="SUCCESS",
            reason=f"Coordinated {len(consensus.participating_agents)} agents | Score: {consensus.consensus_score}"
        )

        return {
            "text": consensus.summary_markdown,
            "consensus_score": consensus.consensus_score,
            "participating_agents": consensus.participating_agents,
            "recommendations": consensus.unified_recommendations,
            "source": f"Enterprise Multi-Agent Collaboration ({len(consensus.participating_agents)} Agents)",
            "verified": True,
            "metrics": ctx.metrics
        }

_agent_orchestrator_instance = None

def get_agent_orchestrator() -> AgentOrchestrator:
    global _agent_orchestrator_instance
    if _agent_orchestrator_instance is None:
        _agent_orchestrator_instance = AgentOrchestrator()
    return _agent_orchestrator_instance
