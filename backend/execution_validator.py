import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from tool_executor import ToolExecutionResult
from execution_planner import ExecutableStep

logger = logging.getLogger(__name__)

class StepValidationResult(BaseModel):
    is_valid: bool
    step_id: str
    tool_name: str
    error_message: Optional[str] = None
    missing_output_keys: List[str] = Field(default_factory=list)

class ExecutionValidator:
    def __init__(self):
        pass

    def validate_step_execution(self, step: ExecutableStep, exec_result: ToolExecutionResult) -> StepValidationResult:
        if not exec_result.success:
            return StepValidationResult(
                is_valid=False,
                step_id=step.step_id,
                tool_name=step.tool_name,
                error_message=exec_result.error_message or "Tool execution reported failure status."
            )

        output = exec_result.output or {}
        missing_keys = []

        for req_key in step.expected_output_keys:
            if req_key not in output:
                missing_keys.append(req_key)

        if missing_keys:
            logger.warning(f"Step '{step.step_id}' execution returned payload missing expected keys: {missing_keys}")
            primary_ids = {"event_id", "lead_id", "ticket_id", "transaction_id", "message_id"}
            if any(k in primary_ids for k in missing_keys):
                return StepValidationResult(
                    is_valid=False,
                    step_id=step.step_id,
                    tool_name=step.tool_name,
                    error_message=f"Missing primary identifier output key: {missing_keys}",
                    missing_output_keys=missing_keys
                )

        return StepValidationResult(
            is_valid=True,
            step_id=step.step_id,
            tool_name=step.tool_name,
            missing_output_keys=missing_keys
        )

_execution_validator_instance = None

def get_execution_validator() -> ExecutionValidator:
    global _execution_validator_instance
    if _execution_validator_instance is None:
        _execution_validator_instance = ExecutionValidator()
    return _execution_validator_instance
