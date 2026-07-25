import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel
from memory_store import EnterpriseMemory

logger = logging.getLogger(__name__)

class MemoryAccessDecision(BaseModel):
    allowed: bool
    memory_id: str
    visibility: str
    requesting_user_id: str
    requesting_user_role: str
    reason: str

class MemoryPermissionEngine:
    def __init__(self):
        pass

    def check_read_access(
        self,
        memory: EnterpriseMemory,
        requesting_user_id: str,
        requesting_org_id: str,
        requesting_user_role: str
    ) -> MemoryAccessDecision:
        role = requesting_user_role.lower()
        vis = memory.visibility.upper()

        if role == "admin":
            return MemoryAccessDecision(
                allowed=True,
                memory_id=memory.memory_id,
                visibility=vis,
                requesting_user_id=requesting_user_id,
                requesting_user_role=role,
                reason="Admin role granted global memory access."
            )

        if vis == "GLOBAL":
            return MemoryAccessDecision(
                allowed=True,
                memory_id=memory.memory_id,
                visibility=vis,
                requesting_user_id=requesting_user_id,
                requesting_user_role=role,
                reason="Global memory is accessible."
            )

        if vis == "ADMIN_ONLY":
            return MemoryAccessDecision(
                allowed=False,
                memory_id=memory.memory_id,
                visibility=vis,
                requesting_user_id=requesting_user_id,
                requesting_user_role=role,
                reason=f"Permission Denied: Memory '{memory.memory_id}' has visibility ADMIN_ONLY."
            )

        if vis == "PRIVATE_USER":
            if requesting_user_id == memory.owner_user_id:
                return MemoryAccessDecision(
                    allowed=True,
                    memory_id=memory.memory_id,
                    visibility=vis,
                    requesting_user_id=requesting_user_id,
                    requesting_user_role=role,
                    reason="Private user memory accessed by owner."
                )
            else:
                return MemoryAccessDecision(
                    allowed=False,
                    memory_id=memory.memory_id,
                    visibility=vis,
                    requesting_user_id=requesting_user_id,
                    requesting_user_role=role,
                    reason=f"Permission Denied: User '{requesting_user_id}' cannot access PRIVATE_USER memory owned by '{memory.owner_user_id}'."
                )

        if vis in ["ORGANIZATION", "TEAM"]:
            if requesting_org_id == memory.organization_id:
                return MemoryAccessDecision(
                    allowed=True,
                    memory_id=memory.memory_id,
                    visibility=vis,
                    requesting_user_id=requesting_user_id,
                    requesting_user_role=role,
                    reason=f"{vis} memory accessed within same organization '{requesting_org_id}'."
                )
            else:
                return MemoryAccessDecision(
                    allowed=False,
                    memory_id=memory.memory_id,
                    visibility=vis,
                    requesting_user_id=requesting_user_id,
                    requesting_user_role=role,
                    reason=f"Permission Denied: Organization '{requesting_org_id}' cannot access {vis} memory of '{memory.organization_id}'."
                )

        return MemoryAccessDecision(
            allowed=False,
            memory_id=memory.memory_id,
            visibility=vis,
            requesting_user_id=requesting_user_id,
            requesting_user_role=role,
            reason="Permission Denied: Unknown visibility policy."
        )

_memory_permission_engine_instance = None

def get_memory_permission_engine() -> MemoryPermissionEngine:
    global _memory_permission_engine_instance
    if _memory_permission_engine_instance is None:
        _memory_permission_engine_instance = MemoryPermissionEngine()
    return _memory_permission_engine_instance
