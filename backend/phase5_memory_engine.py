import logging
from typing import Dict, Any, List, Optional
from orchestration_context import OrchestrationContext
from memory_resolver import get_memory_resolver, ResolvedMemory
from memory_manager import get_memory_manager
from memory_store import EnterpriseMemory

logger = logging.getLogger(__name__)

class Phase5MemoryEngine:
    def __init__(self):
        self.resolver = get_memory_resolver()
        self.manager = get_memory_manager()

    def resolve_context_memories(
        self,
        ctx: OrchestrationContext,
        user_id: str = "user_default",
        organization_id: str = "org_default",
        user_role: str = "sales_agent"
    ) -> List[ResolvedMemory]:
        memories = self.resolver.resolve_relevant_memories(
            user_id=user_id,
            organization_id=organization_id,
            user_role=user_role,
            entity_id=ctx.resolved_entity_id,
            intent=ctx.intent,
            query=ctx.original_query
        )

        ctx.add_trace(
            stage="Phase5MemoryEngine",
            result=f"Resolved {len(memories)} memories",
            reason=f"Memory types: {[m.type for m in memories]}"
        )

        return memories

    def record_user_preference(
        self,
        preference_text: str,
        user_id: str = "user_default",
        organization_id: str = "org_default"
    ) -> Optional[EnterpriseMemory]:
        return self.manager.create_memory(
            content=preference_text,
            owner_user_id=user_id,
            organization_id=organization_id,
            visibility="PRIVATE_USER",
            memory_type="PREFERENCE",
            source_type="MANUAL_USER_INPUT"
        )

    def record_workflow_outcome(
        self,
        workflow_goal: str,
        execution_summary: str,
        user_id: str = "user_default",
        organization_id: str = "org_default"
    ) -> Optional[EnterpriseMemory]:
        return self.manager.create_memory(
            content=f"Workflow Completed: {workflow_goal} - {execution_summary}",
            owner_user_id=user_id,
            organization_id=organization_id,
            visibility="ORGANIZATION",
            memory_type="ACTION",
            source_type="WORKFLOW"
        )

_memory_engine_instance = None

def get_phase5_memory_engine() -> Phase5MemoryEngine:
    global _memory_engine_instance
    if _memory_engine_instance is None:
        _memory_engine_instance = Phase5MemoryEngine()
    return _memory_engine_instance
