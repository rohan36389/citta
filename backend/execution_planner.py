import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from action_planner import ActionPlan, ActionStep

logger = logging.getLogger(__name__)

class DataBinding(BaseModel):
    parameter_name: str
    source_step_id: str
    source_parameter_name: str

class ExecutableStep(BaseModel):
    step_id: str
    step_number: int
    tool_name: str
    operation: str
    raw_parameters: Dict[str, Any] = Field(default_factory=dict)
    data_bindings: List[DataBinding] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    expected_output_keys: List[str] = Field(default_factory=list)

class ExecutableWorkflow(BaseModel):
    workflow_id: str
    goal: str
    steps: List[ExecutableStep] = Field(default_factory=list)

class ExecutionPlanner:
    def __init__(self):
        pass

    def plan_execution(self, action_plan: ActionPlan) -> ExecutableWorkflow:
        executable_steps = []

        for step in action_plan.steps:
            bindings = []
            for param_name, param_val in step.parameters.items():
                if isinstance(param_val, str) and param_val.startswith("{{") and param_val.endswith("}}"):
                    expr = param_val[2:-2].strip()
                    parts = expr.split(".")
                    if len(parts) == 2:
                        bindings.append(DataBinding(
                            parameter_name=param_name,
                            source_step_id=parts[0],
                            source_parameter_name=parts[1]
                        ))

            # Infer expected outputs per tool operation
            exp_outputs = []
            if step.tool_name == "calendar":
                exp_outputs = ["event_id", "status"]
            elif step.tool_name == "crm":
                exp_outputs = ["lead_id", "status"]
            elif step.tool_name == "email":
                exp_outputs = ["message_id", "status"]
            elif step.tool_name == "support_desk":
                exp_outputs = ["ticket_id", "status"]
            elif step.tool_name == "erp":
                exp_outputs = ["transaction_id", "status"]

            executable_steps.append(ExecutableStep(
                step_id=step.step_id,
                step_number=step.step_number,
                tool_name=step.tool_name,
                operation=step.operation,
                raw_parameters=step.parameters,
                data_bindings=bindings,
                prerequisites=step.prerequisites,
                expected_output_keys=exp_outputs
            ))

        return ExecutableWorkflow(
            workflow_id=f"wf_{action_plan.plan_id}",
            goal=action_plan.goal,
            steps=executable_steps
        )

_execution_planner_instance = None

def get_execution_planner() -> ExecutionPlanner:
    global _execution_planner_instance
    if _execution_planner_instance is None:
        _execution_planner_instance = ExecutionPlanner()
    return _execution_planner_instance
