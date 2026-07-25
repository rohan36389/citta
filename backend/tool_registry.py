import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ToolPolicy(BaseModel):
    timeout_sec: float = 30.0
    max_retries: int = 3
    requires_approval: bool = False
    allow_parallel: bool = False

class ToolOperation(BaseModel):
    name: str
    description: str
    required_parameters: List[str] = Field(default_factory=list)
    optional_parameters: List[str] = Field(default_factory=list)
    required_permission: str = "EXECUTE"

class EnterpriseTool(BaseModel):
    name: str
    category: str
    description: str
    capabilities: List[str] = Field(default_factory=list)
    policy: ToolPolicy = Field(default_factory=ToolPolicy)
    operations: Dict[str, ToolOperation] = Field(default_factory=dict)

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, EnterpriseTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        # 1. Calendar Tool
        self.tools["calendar"] = EnterpriseTool(
            name="calendar",
            category="Scheduling",
            description="Enterprise Calendar for demo booking and meeting management",
            capabilities=["schedule_event", "cancel_event", "reschedule_event"],
            policy=ToolPolicy(timeout_sec=15.0, max_retries=3, requires_approval=False),
            operations={
                "schedule_event": ToolOperation(
                    name="schedule_event",
                    description="Schedules a demo or meeting",
                    required_parameters=["title", "date_time", "attendee_email"],
                    optional_parameters=["duration_mins", "description"],
                    required_permission="calendar.write"
                )
            }
        )

        # 2. CRM Tool
        self.tools["crm"] = EnterpriseTool(
            name="crm",
            category="Customer Relationship Management",
            description="Enterprise CRM for lead creation and customer records",
            capabilities=["create_lead", "update_lead", "get_account"],
            policy=ToolPolicy(timeout_sec=10.0, max_retries=3, requires_approval=False),
            operations={
                "create_lead": ToolOperation(
                    name="create_lead",
                    description="Creates a new sales lead",
                    required_parameters=["name", "email"],
                    optional_parameters=["company", "product_interest", "event_id"],
                    required_permission="crm.write"
                )
            }
        )

        # 3. Email Tool
        self.tools["email"] = EnterpriseTool(
            name="email",
            category="Communications",
            description="Enterprise Email Service for sending proposals and confirmations",
            capabilities=["send_email", "send_proposal"],
            policy=ToolPolicy(timeout_sec=20.0, max_retries=3, requires_approval=False),
            operations={
                "send_email": ToolOperation(
                    name="send_email",
                    description="Sends an email message",
                    required_parameters=["recipient_email", "subject", "body"],
                    optional_parameters=["attachment_name", "event_id", "lead_id"],
                    required_permission="email.send"
                )
            }
        )

        # 4. Support Desk Tool
        self.tools["support_desk"] = EnterpriseTool(
            name="support_desk",
            category="Customer Support",
            description="Enterprise Support Ticketing System",
            capabilities=["create_ticket", "update_ticket"],
            policy=ToolPolicy(timeout_sec=15.0, max_retries=3, requires_approval=False),
            operations={
                "create_ticket": ToolOperation(
                    name="create_ticket",
                    description="Creates a new customer support ticket",
                    required_parameters=["product_id", "issue_description"],
                    optional_parameters=["priority", "user_email"],
                    required_permission="support.create"
                )
            }
        )

        # 5. ERP Tool
        self.tools["erp"] = EnterpriseTool(
            name="erp",
            category="Enterprise Resource Planning",
            description="Enterprise ERP for financial and inventory record updates",
            capabilities=["update_record", "financial_transaction"],
            policy=ToolPolicy(timeout_sec=60.0, max_retries=1, requires_approval=True),
            operations={
                "update_record": ToolOperation(
                    name="update_record",
                    description="Updates an ERP financial or operational record",
                    required_parameters=["record_id", "action_code"],
                    optional_parameters=["payload"],
                    required_permission="erp.admin"
                )
            }
        )

    def get_tool(self, tool_name: str) -> Optional[EnterpriseTool]:
        return self.tools.get(tool_name.lower())

_tool_registry_instance = None

def get_tool_registry() -> ToolRegistry:
    global _tool_registry_instance
    if _tool_registry_instance is None:
        _tool_registry_instance = ToolRegistry()
    return _tool_registry_instance
