import logging
from typing import Dict, Any, List, Set, Optional
from pydantic import BaseModel
from execution_context import ExecutionContext
from tool_registry import ToolOperation

logger = logging.getLogger(__name__)

ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "admin": {
        "calendar.write", "crm.write", "email.send", "support.create", "erp.admin", "EXECUTE"
    },
    "sales_agent": {
        "calendar.write", "crm.write", "email.send", "support.create", "EXECUTE"
    },
    "customer_support": {
        "support.create", "email.send", "crm.write", "EXECUTE"
    },
    "guest": {
        "calendar.write", "EXECUTE"
    },
    "restricted_user": set()  # No permissions granted
}

class PermissionCheckResult(BaseModel):
    allowed: bool
    required_permission: str
    user_role: str
    reason: str

class PermissionEngine:
    def __init__(self):
        pass

    def check_permission(self, exec_ctx: ExecutionContext, operation: ToolOperation) -> PermissionCheckResult:
        role = exec_ctx.user_role.lower()
        req_perm = operation.required_permission

        granted_perms = ROLE_PERMISSIONS.get(role, set())

        if req_perm in granted_perms or "admin" in role:
            return PermissionCheckResult(
                allowed=True,
                required_permission=req_perm,
                user_role=role,
                reason=f"Access granted for role '{role}' on permission '{req_perm}'"
            )

        reason_msg = f"Permission Denied: User role '{role}' lacks required permission '{req_perm}' (Scope: WRITE/EXECUTE)."
        logger.warning(reason_msg)
        return PermissionCheckResult(
            allowed=False,
            required_permission=req_perm,
            user_role=role,
            reason=reason_msg
        )

_permission_engine_instance = None

def get_permission_engine() -> PermissionEngine:
    global _permission_engine_instance
    if _permission_engine_instance is None:
        _permission_engine_instance = PermissionEngine()
    return _permission_engine_instance
