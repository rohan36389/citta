import time
import re
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class StepExecutionState(BaseModel):
    step_id: str
    tool_name: str
    operation: str
    status: str = "PENDING"  # PENDING, EXECUTING, SUCCESS, FAILED, BLOCKED
    input_parameters: Dict[str, Any] = Field(default_factory=dict)
    output_payload: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: float = 0.0
    error_message: Optional[str] = None

class ExecutionContext(BaseModel):
    session_id: str
    user_id: str = "user_default"
    user_role: str = "sales_agent"  # admin, sales_agent, customer_support, guest, restricted_user
    organization_id: str = "org_default"
    
    current_step_index: int = 0
    completed_step_ids: List[str] = Field(default_factory=list)
    step_outputs: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    step_states: Dict[str, StepExecutionState] = Field(default_factory=dict)
    
    failures: List[Dict[str, Any]] = Field(default_factory=list)
    retries: Dict[str, int] = Field(default_factory=dict)
    is_blocked: bool = False
    block_reason: Optional[str] = None
    created_at_ms: float = Field(default_factory=lambda: round(time.time() * 1000, 2))

    def bind_parameters(self, raw_params: Dict[str, Any]) -> Dict[str, Any]:
        """Resolves template placeholders like '{{step_1.event_id}}' from step_outputs."""
        resolved = {}
        for key, value in raw_params.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                expr = value[2:-2].strip()  # e.g. "step_1.event_id"
                parts = expr.split(".")
                if len(parts) == 2:
                    step_id, param_name = parts[0], parts[1]
                    if step_id in self.step_outputs and param_name in self.step_outputs[step_id]:
                        resolved[key] = self.step_outputs[step_id][param_name]
                    else:
                        resolved[key] = f"bound_{param_name}_placeholder"
                else:
                    resolved[key] = value
            else:
                resolved[key] = value
        return resolved

    def record_step_success(self, step_id: str, output: Dict[str, Any], latency_ms: float = 0.0):
        self.completed_step_ids.append(step_id)
        self.step_outputs[step_id] = output
        if step_id in self.step_states:
            self.step_states[step_id].status = "SUCCESS"
            self.step_states[step_id].output_payload = output
            self.step_states[step_id].latency_ms = latency_ms

    def record_step_failure(self, step_id: str, error_msg: str, latency_ms: float = 0.0):
        self.failures.append({"step_id": step_id, "error": error_msg, "timestamp_ms": round(time.time() * 1000, 2)})
        if step_id in self.step_states:
            self.step_states[step_id].status = "FAILED"
            self.step_states[step_id].error_message = error_msg
            self.step_states[step_id].latency_ms = latency_ms
