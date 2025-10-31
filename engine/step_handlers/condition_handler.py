import ast
import operator
from typing import TYPE_CHECKING, Any, Dict
from engine.step_handlers.base import BaseStepHandler
from engine.expression_evaluator import evaluate_expression, ExpressionError
from engine.results import StepResult

if TYPE_CHECKING:
    from models.state import StateManager
    from models.workflow import ConditionalStep
    from engine.executor import PulsarEngine

class ConditionEvaluator:
    """Safe condition evaluator for if statements."""

    def __init__(self, state: Dict[str, Any]):
        self.state = state

    def evaluate(self, condition: str) -> bool:
        """Safely evaluate a condition string."""
        try:
            # Use the new advanced expression evaluator
            result = evaluate_expression(condition, self.state)
            return bool(result)
        except ExpressionError as e:
            raise ValueError(f"Invalid condition '{condition}': {e}")
        except Exception as e:
            raise ValueError(f"Condition evaluation failed '{condition}': {e}")

class ConditionStepHandler(BaseStepHandler):
    """Handler for executing conditional steps."""

    def __init__(self, state_manager: "StateManager", executor: "PulsarEngine"):
        super().__init__(state_manager)
        self.executor = executor

    async def can_handle(self, step) -> bool:
        """Check if step is a conditional step."""
        return hasattr(step, 'type') and step.type == "conditional"

    async def execute(self, step: "ConditionalStep") -> StepResult:
        """Execute a conditional step."""
        from models.workflow import ConditionalStep
        if not isinstance(step, ConditionalStep):
            raise ValueError(f"ConditionStepHandler can only handle ConditionalStep, got {type(step)}")
            
        try:
            # Get current state for evaluation
            current_state = await self.state_manager.get_state_snapshot()

            # Evaluate condition
            evaluator = ConditionEvaluator(current_state)
            condition_result = evaluator.evaluate(step.if_)

            # Choose branch
            if condition_result:
                steps_to_execute = step.then
                branch = "then"
            else:
                steps_to_execute = step.else_ or []
                branch = "else"

            # Execute the chosen branch
            branch_results = []
            for sub_step in steps_to_execute:
                result = await self.executor.execute_step(sub_step)
                branch_results.append(result)
                if not result.success:
                    break  # Stop on first failure

            # Check if all steps succeeded
            all_success = all(r.success for r in branch_results)

            metadata = {
                "condition": step.if_,
                "condition_result": condition_result,
                "branch_taken": branch,
                "steps_executed": len(branch_results),
                "branch_results": [r.model_dump() for r in branch_results]
            }

            return await self._create_step_result(
                step_name=step.step,
                success=all_success,
                output={"condition_result": condition_result, "branch": branch},
                metadata=metadata
            )

        except Exception as e:
            error_msg = f"Condition evaluation failed: {str(e)}"
            return await self._create_step_result(
                step_name=step.step,
                success=False,
                error=error_msg,
                metadata={"exception_type": type(e).__name__}
            )