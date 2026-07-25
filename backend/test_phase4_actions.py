import pytest
import asyncio
from orchestration_context import ExecutionStrategy
from phase2_orchestrator import get_phase2_orchestrator
from phase4_action_engine import get_phase4_action_engine
from audit_logger import get_audit_logger

@pytest.fixture
def orchestrator():
    return get_phase2_orchestrator()

@pytest.fixture
def action_engine():
    return get_phase4_action_engine()

def test_schedule_demo_action_workflow(orchestrator, action_engine):
    """Schedule a demo next Tuesday for john@acme.com."""
    async def run_test():
        ctx = orchestrator.orchestrate("p4_sess_01", "Schedule a demo next Tuesday for john@acme.com.", "schedule a demo next tuesday for john@acme.com")
        assert ctx.execution_strategy == ExecutionStrategy.ACTION
        
        result = await action_engine.execute_action_pipeline(ctx, user_role="sales_agent")
        assert result["verified"] is True
        assert result["status"] == "SUCCESS"
        assert "Calendar Event Scheduled" in result["text"]
        assert "CRM Lead Created" in result["text"]
        assert "Email Sent" in result["text"]
        assert len(result["outputs"]) == 3
    asyncio.run(run_test())

def test_create_ticket_action_workflow(orchestrator, action_engine):
    """Create a support ticket for Pharma OS: API error in sync."""
    async def run_test():
        ctx = orchestrator.orchestrate("p4_sess_02", "Create a support ticket for Pharma OS: API error in sync.", "create a support ticket for pharma os api error in sync")
        assert ctx.execution_strategy == ExecutionStrategy.ACTION
        
        result = await action_engine.execute_action_pipeline(ctx, user_role="customer_support")
        assert result["verified"] is True
        assert result["status"] == "SUCCESS"
        assert "Support Ticket Created" in result["text"]
        assert "TICKET_" in result["text"]
    asyncio.run(run_test())

def test_send_proposal_action_workflow(orchestrator, action_engine):
    """Send proposal to ABC Corp at sarah@abccorp.com."""
    async def run_test():
        ctx = orchestrator.orchestrate("p4_sess_03", "Send proposal to ABC Corp at sarah@abccorp.com.", "send proposal to abc corp at sarah@abccorp.com")
        assert ctx.execution_strategy == ExecutionStrategy.ACTION
        
        result = await action_engine.execute_action_pipeline(ctx, user_role="sales_agent")
        assert result["verified"] is True
        assert result["status"] == "SUCCESS"
        assert "Email Sent" in result["text"]
    asyncio.run(run_test())

def test_permission_denied_blocking(orchestrator, action_engine):
    """Restricted user attempting write/admin operation -> Execution blocked by Permission Engine"""
    async def run_test():
        ctx = orchestrator.orchestrate("p4_sess_04", "Schedule a demo next Tuesday for john@acme.com.", "schedule a demo next tuesday for john@acme.com")
        assert ctx.execution_strategy == ExecutionStrategy.ACTION
        
        # User role: restricted_user (has zero write permissions)
        result = await action_engine.execute_action_pipeline(ctx, user_role="restricted_user")
        assert result["verified"] is False
        assert result["status"] == "BLOCKED"
        assert "Permission Denied" in result["text"]
    asyncio.run(run_test())

def test_api_error_retry_and_audit(orchestrator, action_engine):
    """Simulated external API error -> Retries, fallback, and immutable audit log entry recorded"""
    async def run_test():
        ctx = orchestrator.orchestrate("p4_sess_05", "Send proposal to ABC Corp at sarah@abccorp.com.", "send proposal to abc corp at sarah@abccorp.com")
        
        audit_count_before = len(get_audit_logger().audit_records)
        result = await action_engine.execute_action_pipeline(ctx, user_role="sales_agent", simulate_error_on_step="step_1")
        audit_count_after = len(get_audit_logger().audit_records)
        
        assert audit_count_after > audit_count_before
        assert result["verified"] is True  # Succeeded after retries
    asyncio.run(run_test())
