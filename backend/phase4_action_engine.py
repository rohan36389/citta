import time
import logging
from typing import Dict, Any, List, Optional

from orchestration_context import OrchestrationContext
from execution_context import ExecutionContext, StepExecutionState
from action_planner import get_action_planner
from execution_planner import get_execution_planner
from tool_selector import get_tool_selector
from permission_engine import get_permission_engine
from tool_executor import get_tool_executor
from execution_validator import get_execution_validator
from result_aggregator import get_result_aggregator
from audit_logger import get_audit_logger

logger = logging.getLogger(__name__)

class Phase4ActionEngine:
    def __init__(self):
        self.action_planner = get_action_planner()
        self.execution_planner = get_execution_planner()
        self.tool_selector = get_tool_selector()
        self.permission_engine = get_permission_engine()
        self.tool_executor = get_tool_executor()
        self.validator = get_execution_validator()
        self.aggregator = get_result_aggregator()
        self.audit_logger = get_audit_logger()

    async def execute_action_pipeline(
        self,
        ctx: OrchestrationContext,
        user_role: str = "sales_agent",
        simulate_error_on_step: Optional[str] = None
    ) -> Dict[str, Any]:
        start_time = time.time()

        # 1. Action Planner
        action_plan = self.action_planner.plan_action(ctx)

        # 2. Execution Planner (DAG & Parameter Bindings)
        workflow = self.execution_planner.plan_execution(action_plan)

        # 3. Tool Selector
        tool_bindings = self.tool_selector.select_tools_for_workflow(workflow)
        binding_by_step = {b.step_id: b for b in tool_bindings}

        # 4. Initialize ExecutionContext
        exec_ctx = ExecutionContext(
            session_id=ctx.session_id,
            user_id="user_demo",
            user_role=user_role,
            organization_id="org_citta"
        )

        for step in workflow.steps:
            exec_ctx.step_states[step.step_id] = StepExecutionState(
                step_id=step.step_id,
                tool_name=step.tool_name,
                operation=step.operation
            )

        # 5. Execute Steps in Order
        for step in workflow.steps:
            binding = binding_by_step[step.step_id]

            # 5a. Permission Engine Check
            perm_res = self.permission_engine.check_permission(exec_ctx, binding.operation)
            if not perm_res.allowed:
                exec_ctx.is_blocked = True
                exec_ctx.block_reason = perm_res.reason
                exec_ctx.step_states[step.step_id].status = "BLOCKED"
                
                self.audit_logger.log_execution(
                    session_id=ctx.session_id,
                    user_id=exec_ctx.user_id,
                    user_role=exec_ctx.user_role,
                    organization_id=exec_ctx.organization_id,
                    action_goal=workflow.goal,
                    step_id=step.step_id,
                    tool_name=step.tool_name,
                    operation_name=step.operation,
                    parameters=step.raw_parameters,
                    status="BLOCKED_PERMISSION",
                    error_message=perm_res.reason
                )
                break

            # 5b. Resolve Parameter Bindings from ExecutionContext
            bound_params = exec_ctx.bind_parameters(step.raw_parameters)

            # 5c. Tool Executor API Call (with Retries & Policies)
            sim_err = (simulate_error_on_step == step.step_id)
            exec_res = await self.tool_executor.execute_tool_operation(
                step_id=step.step_id,
                tool=binding.tool,
                operation=binding.operation,
                parameters=bound_params,
                exec_ctx=exec_ctx,
                simulate_error=sim_err
            )

            # 5d. Execution Validator Check
            val_res = self.validator.validate_step_execution(step, exec_res)

            if val_res.is_valid:
                exec_ctx.record_step_success(step.step_id, exec_res.output, exec_res.latency_ms)
                self.audit_logger.log_execution(
                    session_id=ctx.session_id,
                    user_id=exec_ctx.user_id,
                    user_role=exec_ctx.user_role,
                    organization_id=exec_ctx.organization_id,
                    action_goal=workflow.goal,
                    step_id=step.step_id,
                    tool_name=step.tool_name,
                    operation_name=step.operation,
                    parameters=bound_params,
                    status="SUCCESS",
                    latency_ms=exec_res.latency_ms
                )
            else:
                exec_ctx.record_step_failure(step.step_id, val_res.error_message or "Validation failed", exec_res.latency_ms)
                self.audit_logger.log_execution(
                    session_id=ctx.session_id,
                    user_id=exec_ctx.user_id,
                    user_role=exec_ctx.user_role,
                    organization_id=exec_ctx.organization_id,
                    action_goal=workflow.goal,
                    step_id=step.step_id,
                    tool_name=step.tool_name,
                    operation_name=step.operation,
                    parameters=bound_params,
                    status="FAILED",
                    latency_ms=exec_res.latency_ms,
                    error_message=val_res.error_message
                )
                break

        # 6. Result Aggregator
        aggregated = self.aggregator.aggregate_results(exec_ctx, workflow.goal)
        latency_ms = round((time.time() - start_time) * 1000.0, 2)

        # Update Context Metrics & Response
        ctx.response_text = aggregated["summary"]
        ctx.metrics["action_goal"] = workflow.goal
        ctx.metrics["action_status"] = aggregated["status"]
        ctx.metrics["actions_executed"] = aggregated.get("actions_executed", [])
        ctx.metrics["latency_ms"] = latency_ms

        ctx.add_trace(
            stage="Phase4ActionEngine",
            result=aggregated["status"],
            reason=f"Goal: {workflow.goal} | Executed: {len(exec_ctx.completed_step_ids)} steps"
        )

        return {
            "text": aggregated["summary"],
            "status": aggregated["status"],
            "source": f"Enterprise Action Platform ({workflow.goal})",
            "verified": aggregated["verified"],
            "outputs": aggregated["outputs"],
            "suggestions": [
                "View action audit log",
                "Check CRM lead status",
                "View calendar events"
            ],
            "metrics": ctx.metrics
        }

_action_engine_instance = None

def get_phase4_action_engine() -> Phase4ActionEngine:
    global _action_engine_instance
    if _action_engine_instance is None:
        _action_engine_instance = Phase4ActionEngine()
    return _action_engine_instance
