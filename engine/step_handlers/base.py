from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from engine.results import StepResult

if TYPE_CHECKING:
    from models.state import StateManager
    from models.workflow import Step

class BaseStepHandler(ABC):
    """Abstract base class for step handlers."""

    def __init__(self, state_manager: "StateManager"):
        self.state_manager = state_manager

    @abstractmethod
    async def can_handle(self, step: "Step") -> bool:
        """Check if this handler can process the given step."""
        pass

    @abstractmethod
    async def execute(self, step: "Step") -> StepResult:
        """Execute the step and return result."""
        pass

    async def _create_step_result(self, step_name: str, success: bool, output=None, error=None, metadata=None) -> StepResult:
        """Helper to create StepResult with timing."""
        import time
        from datetime import datetime

        started_at = datetime.now()
        start_time = time.time()

        # Simulate execution time (in real implementation, this would wrap the actual execution)
        if success:
            execution_time = time.time() - start_time
            completed_at = datetime.now()
        else:
            execution_time = time.time() - start_time
            completed_at = datetime.now()

        return StepResult(
            step_name=step_name,
            success=success,
            output=output,
            error=error,
            execution_time=execution_time,
            started_at=started_at,
            completed_at=completed_at,
            metadata=metadata or {}
        )