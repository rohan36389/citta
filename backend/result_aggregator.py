import logging
from typing import Dict, Any, List, Optional
from execution_context import ExecutionContext

logger = logging.getLogger(__name__)

class ResultAggregator:
    def __init__(self):
        pass

    def aggregate_results(self, exec_ctx: ExecutionContext, goal: str) -> Dict[str, Any]:
        if exec_ctx.is_blocked:
            return {
                "status": "BLOCKED",
                "summary": f"Execution Blocked: {exec_ctx.block_reason}",
                "completed_steps": exec_ctx.completed_step_ids,
                "outputs": exec_ctx.step_outputs,
                "verified": False
            }

        if exec_ctx.failures:
            first_fail = exec_ctx.failures[0]
            return {
                "status": "FAILED",
                "summary": f"Execution Failed on step '{first_fail.get('step_id')}': {first_fail.get('error')}",
                "completed_steps": exec_ctx.completed_step_ids,
                "outputs": exec_ctx.step_outputs,
                "verified": False
            }

        lines = [f"### Workflow Executed Successfully: {goal}\n"]
        formatted_actions = []

        for step_id, out in exec_ctx.step_outputs.items():
            if "lead_id" in out:
                lead_id = out.get("lead_id")
                company = out.get("company", "Lead")
                lines.append(f"✓ **CRM Lead Created**: Lead ID `{lead_id}` for {company}")
                formatted_actions.append(f"CRM Lead ({lead_id})")

            elif "event_id" in out:
                evt_id = out.get("event_id")
                date_time = out.get("date_time", "Scheduled Time")
                lines.append(f"✓ **Calendar Event Scheduled**: Event ID `{evt_id}` ({date_time})")
                formatted_actions.append(f"Calendar Event ({evt_id})")

            elif "message_id" in out:
                msg_id = out.get("message_id")
                recipient = out.get("recipient", "Client")
                lines.append(f"✓ **Email Sent**: Message ID `{msg_id}` to {recipient}")
                formatted_actions.append(f"Email Sent ({msg_id})")

            elif "ticket_id" in out:
                ticket_id = out.get("ticket_id")
                team = out.get("assigned_team", "Support Team")
                lines.append(f"✓ **Support Ticket Created**: Ticket ID `{ticket_id}` (Assigned to {team})")
                formatted_actions.append(f"Support Ticket ({ticket_id})")

            elif "transaction_id" in out:
                tx_id = out.get("transaction_id")
                lines.append(f"✓ **ERP Record Updated**: Transaction ID `{tx_id}`")
                formatted_actions.append(f"ERP Record ({tx_id})")

        return {
            "status": "SUCCESS",
            "summary": "\n".join(lines),
            "actions_executed": formatted_actions,
            "completed_steps": exec_ctx.completed_step_ids,
            "outputs": exec_ctx.step_outputs,
            "verified": True
        }

_result_aggregator_instance = None

def get_result_aggregator() -> ResultAggregator:
    global _result_aggregator_instance
    if _result_aggregator_instance is None:
        _result_aggregator_instance = ResultAggregator()
    return _result_aggregator_instance
