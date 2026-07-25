import logging
from typing import Dict, Any, List, Optional
from orchestration_context import OrchestrationContext
from agent_orchestrator import get_agent_orchestrator

logger = logging.getLogger(__name__)

class Phase6CollaborationEngine:
    def __init__(self):
        self.orchestrator = get_agent_orchestrator()

    async def execute_collaboration_pipeline(
        self,
        ctx: OrchestrationContext,
        simulate_failure_agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        return await self.orchestrator.orchestrate_collaboration(
            ctx=ctx,
            simulate_failure_agent_id=simulate_failure_agent_id
        )

_phase6_engine_instance = None

def get_phase6_collaboration_engine() -> Phase6CollaborationEngine:
    global _phase6_engine_instance
    if _phase6_engine_instance is None:
        _phase6_engine_instance = Phase6CollaborationEngine()
    return _phase6_engine_instance
