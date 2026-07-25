import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from tool_registry import get_tool_registry, EnterpriseTool, ToolOperation
from execution_planner import ExecutableStep, ExecutableWorkflow

logger = logging.getLogger(__name__)

class SelectedToolBinding(BaseModel):
    step_id: str
    tool_name: str
    operation_name: str
    tool: EnterpriseTool
    operation: ToolOperation
    validated_parameters: Dict[str, Any]

class ToolSelector:
    def __init__(self):
        self.registry = get_tool_registry()

    def select_tools_for_workflow(self, workflow: ExecutableWorkflow) -> List[SelectedToolBinding]:
        bindings = []

        for step in workflow.steps:
            tool = self.registry.get_tool(step.tool_name)
            if not tool:
                raise ValueError(f"Tool '{step.tool_name}' not registered in Enterprise Tool Registry.")

            if step.operation not in tool.operations:
                raise ValueError(f"Operation '{step.operation}' not supported by tool '{step.tool_name}'.")

            op = tool.operations[step.operation]

            # Validate required parameters (allowing data bindings to satisfy missing raw values)
            bound_param_names = {b.parameter_name for b in step.data_bindings}
            missing_reqs = []
            for req in op.required_parameters:
                if req not in step.raw_parameters and req not in bound_param_names:
                    missing_reqs.append(req)

            if missing_reqs:
                logger.warning(f"Step '{step.step_id}' missing required parameters for operation '{step.operation}': {missing_reqs}")

            bindings.append(SelectedToolBinding(
                step_id=step.step_id,
                tool_name=step.tool_name,
                operation_name=step.operation,
                tool=tool,
                operation=op,
                validated_parameters=step.raw_parameters
            ))

        return bindings

_tool_selector_instance = None

def get_tool_selector() -> ToolSelector:
    global _tool_selector_instance
    if _tool_selector_instance is None:
        _tool_selector_instance = ToolSelector()
    return _tool_selector_instance
