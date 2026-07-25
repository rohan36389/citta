import os
import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

AUDIT_LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
AUDIT_LOG_FILE = os.path.join(AUDIT_LOG_DIR, "audit_trail.jsonl")

class AuditRecord(BaseModel):
    timestamp_iso: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    session_id: str
    user_id: str
    user_role: str
    organization_id: str
    action_goal: str
    step_id: str
    tool_name: str
    operation_name: str
    sanitized_parameters: Dict[str, Any] = Field(default_factory=dict)
    status: str  # SUCCESS, FAILED, BLOCKED_PERMISSION
    latency_ms: float = 0.0
    error_message: Optional[str] = None

class AuditLogger:
    def __init__(self):
        self.audit_records: List[AuditRecord] = []
        self._ensure_log_dir()

    def _ensure_log_dir(self):
        try:
            os.makedirs(AUDIT_LOG_DIR, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create audit log directory: {e}")

    def sanitize_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Strips sensitive credentials/tokens/passwords from audit logs."""
        sanitized = {}
        sensitive_keys = {"password", "token", "secret", "api_key", "credit_card"}
        for k, v in params.items():
            if any(s in k.lower() for s in sensitive_keys):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = v
        return sanitized

    def log_execution(
        self,
        session_id: str,
        user_id: str,
        user_role: str,
        organization_id: str,
        action_goal: str,
        step_id: str,
        tool_name: str,
        operation_name: str,
        parameters: Dict[str, Any],
        status: str,
        latency_ms: float = 0.0,
        error_message: Optional[str] = None
    ) -> AuditRecord:
        record = AuditRecord(
            session_id=session_id,
            user_id=user_id,
            user_role=user_role,
            organization_id=organization_id,
            action_goal=action_goal,
            step_id=step_id,
            tool_name=tool_name,
            operation_name=operation_name,
            sanitized_parameters=self.sanitize_parameters(parameters),
            status=status,
            latency_ms=latency_ms,
            error_message=error_message
        )
        self.audit_records.append(record)

        # Write to JSONL file
        try:
            with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record.model_dump()) + "\n")
        except Exception as e:
            logger.error(f"Failed to append to audit log file: {e}")

        return record

_audit_logger_instance = None

def get_audit_logger() -> AuditLogger:
    global _audit_logger_instance
    if _audit_logger_instance is None:
        _audit_logger_instance = AuditLogger()
    return _audit_logger_instance
