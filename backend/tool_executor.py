import time
import uuid
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from tool_registry import EnterpriseTool, ToolOperation
from execution_context import ExecutionContext

logger = logging.getLogger(__name__)

class ToolExecutionResult(BaseModel):
    step_id: str
    tool_name: str
    operation_name: str
    success: bool
    output: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    retry_count: int = 0
    latency_ms: float = 0.0

class ToolExecutor:
    def __init__(self):
        pass

    async def execute_tool_operation(
        self,
        step_id: str,
        tool: EnterpriseTool,
        operation: ToolOperation,
        parameters: Dict[str, Any],
        exec_ctx: ExecutionContext,
        simulate_error: bool = False
    ) -> ToolExecutionResult:
        start_time = time.time()
        max_retries = tool.policy.max_retries
        attempts = 0
        last_error = None

        while attempts < max_retries:
            attempts += 1
            try:
                if simulate_error and attempts < max_retries:
                    raise ConnectionError("Simulated external API temporary timeout.")

                # Execute mock connector operation
                output = self._dispatch_mock_connector(tool.name, operation.name, parameters)
                latency = round((time.time() - start_time) * 1000.0, 2)
                
                return ToolExecutionResult(
                    step_id=step_id,
                    tool_name=tool.name,
                    operation_name=operation.name,
                    success=True,
                    output=output,
                    retry_count=attempts - 1,
                    latency_ms=latency
                )

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Tool execution attempt {attempts}/{max_retries} failed for '{tool.name}.{operation.name}': {e}")
                if attempts >= max_retries:
                    break

        latency = round((time.time() - start_time) * 1000.0, 2)
        return ToolExecutionResult(
            step_id=step_id,
            tool_name=tool.name,
            operation_name=operation.name,
            success=False,
            error_message=last_error or "API execution failed after retries",
            retry_count=attempts - 1,
            latency_ms=latency
        )

    def _dispatch_mock_connector(self, tool_name: str, op_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        uid = str(uuid.uuid4())[:8]

        if tool_name == "calendar" and op_name == "schedule_event":
            return {
                "event_id": f"evt_{uid}",
                "status": "CONFIRMED",
                "title": params.get("title", "Product Demo"),
                "date_time": params.get("date_time", "Scheduled Time"),
                "calendar_link": f"https://cal.citta.ai/evt_{uid}"
            }

        elif tool_name == "crm" and op_name == "create_lead":
            return {
                "lead_id": f"lead_{uid}",
                "status": "CREATED",
                "name": params.get("name", "Prospect"),
                "company": params.get("company", "Acme Corp"),
                "event_id": params.get("event_id", "N/A")
            }

        elif tool_name == "email" and op_name == "send_email":
            return {
                "message_id": f"msg_{uid}",
                "status": "SENT",
                "recipient": params.get("recipient_email", "prospect@acme.com"),
                "subject": params.get("subject", "Confirmation")
            }

        elif tool_name == "support_desk" and op_name == "create_ticket":
            return {
                "ticket_id": f"TICKET_{uid.upper()}",
                "status": "OPEN",
                "product_id": params.get("product_id", "pharma_os"),
                "priority": params.get("priority", "HIGH"),
                "assigned_team": "Tier-2 Technical Support"
            }

        elif tool_name == "erp" and op_name == "update_record":
            return {
                "transaction_id": f"tx_{uid}",
                "status": "COMPLETED",
                "record_id": params.get("record_id", "REC_9001"),
                "action_code": params.get("action_code", "UPDATE")
            }

        return {"status": "SUCCESS", "execution_id": f"exec_{uid}"}

_tool_executor_instance = None

def get_tool_executor() -> ToolExecutor:
    global _tool_executor_instance
    if _tool_executor_instance is None:
        _tool_executor_instance = ToolExecutor()
    return _tool_executor_instance
