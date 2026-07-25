import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from orchestration_context import OrchestrationContext, EnterpriseIntent

logger = logging.getLogger(__name__)

class ActionStep(BaseModel):
    step_id: str
    step_number: int
    tool_name: str
    operation: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    prerequisites: List[str] = Field(default_factory=list)

class ActionPlan(BaseModel):
    plan_id: str
    goal: str
    steps: List[ActionStep] = Field(default_factory=list)
    raw_query: str

class ActionPlanner:
    def __init__(self):
        pass

    def plan_action(self, ctx: OrchestrationContext) -> ActionPlan:
        q_lower = ctx.normalized_query.lower().strip()
        plan_id = f"plan_{ctx.session_id}_{int(ctx.confidence * 1000)}"

        # 1. Schedule Demo Workflow
        if "schedule" in q_lower or "demo" in q_lower or "book" in q_lower:
            # Extract email if present
            import re
            email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", ctx.original_query)
            attendee_email = email_match.group(0) if email_match else "prospect@acme.com"

            return ActionPlan(
                plan_id=plan_id,
                goal="Schedule Product Demo and Onboard Lead",
                raw_query=ctx.original_query,
                steps=[
                    ActionStep(
                        step_id="step_1",
                        step_number=1,
                        tool_name="calendar",
                        operation="schedule_event",
                        parameters={
                            "title": f"CittaAI Product Demo - {ctx.resolved_entity_name or 'Enterprise OS'}",
                            "date_time": "Next Tuesday at 10:00 AM",
                            "attendee_email": attendee_email,
                            "duration_mins": 45
                        }
                    ),
                    ActionStep(
                        step_id="step_2",
                        step_number=2,
                        tool_name="crm",
                        operation="create_lead",
                        parameters={
                            "name": attendee_email.split("@")[0].capitalize(),
                            "email": attendee_email,
                            "company": attendee_email.split("@")[1].split(".")[0].upper() if "@" in attendee_email else "Acme Corp",
                            "product_interest": ctx.resolved_entity_name or "Enterprise OS",
                            "event_id": "{{step_1.event_id}}"
                        },
                        prerequisites=["step_1"]
                    ),
                    ActionStep(
                        step_id="step_3",
                        step_number=3,
                        tool_name="email",
                        operation="send_email",
                        parameters={
                            "recipient_email": attendee_email,
                            "subject": "Confirmation: Your CittaAI Demo is Scheduled",
                            "body": "Thank you for scheduling a demo. Your event details are confirmed.",
                            "event_id": "{{step_1.event_id}}",
                            "lead_id": "{{step_2.lead_id}}"
                        },
                        prerequisites=["step_1", "step_2"]
                    )
                ]
            )

        # 2. Support Ticket Workflow
        elif "ticket" in q_lower or "issue" in q_lower or "bug" in q_lower or "support" in q_lower:
            return ActionPlan(
                plan_id=plan_id,
                goal="Create Customer Support Ticket",
                raw_query=ctx.original_query,
                steps=[
                    ActionStep(
                        step_id="step_1",
                        step_number=1,
                        tool_name="support_desk",
                        operation="create_ticket",
                        parameters={
                            "product_id": ctx.resolved_entity_id or "pharma_os",
                            "issue_description": ctx.original_query,
                            "priority": "HIGH"
                        }
                    )
                ]
            )

        # 3. Send Proposal Workflow
        elif "proposal" in q_lower or "send proposal" in q_lower:
            import re
            email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", ctx.original_query)
            recipient = email_match.group(0) if email_match else "client@abccorp.com"

            return ActionPlan(
                plan_id=plan_id,
                goal="Generate and Send Enterprise Proposal",
                raw_query=ctx.original_query,
                steps=[
                    ActionStep(
                        step_id="step_1",
                        step_number=1,
                        tool_name="email",
                        operation="send_email",
                        parameters={
                            "recipient_email": recipient,
                            "subject": f"CittaAI Enterprise Proposal - {ctx.resolved_entity_name or 'Solution'}",
                            "body": "Please find attached our formal enterprise proposal for your review.",
                            "attachment_name": "CittaAI_Enterprise_Proposal.pdf"
                        }
                    )
                ]
            )

        # 4. ERP Administrative Action Workflow
        elif "erp" in q_lower or "financial" in q_lower or "record" in q_lower:
            return ActionPlan(
                plan_id=plan_id,
                goal="Update Enterprise ERP Record",
                raw_query=ctx.original_query,
                steps=[
                    ActionStep(
                        step_id="step_1",
                        step_number=1,
                        tool_name="erp",
                        operation="update_record",
                        parameters={
                            "record_id": "REC_9001",
                            "action_code": "FINANCIAL_UPDATE"
                        }
                    )
                ]
            )

        # Default Fallback Action Plan
        return ActionPlan(
            plan_id=plan_id,
            goal="Execute General Action Request",
            raw_query=ctx.original_query,
            steps=[
                ActionStep(
                    step_id="step_1",
                    step_number=1,
                    tool_name="crm",
                    operation="create_lead",
                    parameters={
                        "name": "General Prospect",
                        "email": "prospect@citta.ai"
                    }
                )
            ]
        )

_action_planner_instance = None

def get_action_planner() -> ActionPlanner:
    global _action_planner_instance
    if _action_planner_instance is None:
        _action_planner_instance = ActionPlanner()
    return _action_planner_instance
