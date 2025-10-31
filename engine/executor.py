import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from models.state import StateManager
from models.workflow import Workflow
from engine.results import ExecutionResult, StepResult
from engine.step_handlers.agent_handler import AgentStepHandler
from engine.step_handlers.condition_handler import ConditionStepHandler
from engine.step_handlers.interaction_handler import InteractionStepHandler
from agents import AgentFactory, PulsarConfig

class PulsarEngine:
    """Main workflow execution engine for Pulsar."""

    def __init__(self, workflow: Workflow, config: Optional[PulsarConfig] = None):
        self.workflow = workflow
        self.config = config or PulsarConfig.from_env()
        self.agent_factory = AgentFactory(self.config)
        self.state_manager = StateManager()
        self.step_handlers = [
            AgentStepHandler(self.state_manager, self.agent_factory, self.workflow.agents),
            ConditionStepHandler(self.state_manager, self),
            InteractionStepHandler(self.state_manager)
        ]

    async def execute(self, user_input: str = "") -> ExecutionResult:
        """Execute the workflow with given input."""
        return await self.execute_with_initial_state({"input": user_input})

    async def execute_with_initial_state(self, initial_state: Dict[str, Any]) -> ExecutionResult:
        """Execute the workflow with given initial state."""
        start_time = time.time()
        started_at = datetime.now()

        try:
            # Initialize state - preserve existing state if present
            existing_state = {}
            if hasattr(self, 'state_manager') and self.state_manager:
                try:
                    existing_state = await self.state_manager.get_state_snapshot()
                except:
                    existing_state = {}
            
            # Merge existing state with initial state
            initial_state.update(existing_state)
            self.state_manager = StateManager(initial_state)

            # Reinitialize handlers with new state
            self.step_handlers = [
                AgentStepHandler(self.state_manager, self.agent_factory, self.workflow.agents),
                ConditionStepHandler(self.state_manager, self),
                InteractionStepHandler(self.state_manager)
            ]

            step_results = []

            # Execute each step
            for step in self.workflow.workflow:
                result = await self.execute_step(step)
                step_results.append(result)

                # Stop on failure unless step allows continuation
                if not result.success:
                    break

            # Collect final state
            final_state = await self.state_manager.get_state_snapshot()
            execution_history = await self.state_manager.get_execution_history()

            success = all(r.success for r in step_results)
            total_time = time.time() - start_time
            completed_at = datetime.now()

            return ExecutionResult(
                workflow_name=self.workflow.name,
                success=success,
                final_state=final_state,
                step_results=step_results,
                total_execution_time=total_time,
                started_at=started_at,
                completed_at=completed_at,
                execution_history=execution_history
            )

        except Exception as e:
            total_time = time.time() - start_time
            completed_at = datetime.now()
            final_state = await self.state_manager.get_state_snapshot()
            execution_history = await self.state_manager.get_execution_history()

            return ExecutionResult(
                workflow_name=self.workflow.name,
                success=False,
                final_state=final_state,
                step_results=[],
                total_execution_time=total_time,
                started_at=started_at,
                completed_at=completed_at,
                error=str(e),
                execution_history=execution_history
            )

    async def execute_step(self, step) -> StepResult:
        """Execute a single step using appropriate handler."""
        # Find handler for this step
        for handler in self.step_handlers:
            if await handler.can_handle(step):
                return await handler.execute(step)

        # No handler found
        return StepResult(
            step_name=getattr(step, 'step', 'unknown'),
            success=False,
            error=f"No handler found for step type: {getattr(step, 'type', 'unknown')}",
            execution_time=0.0,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            metadata={}
        )

    def get_current_state(self) -> Dict[str, Any]:
        """Get current execution state (synchronous snapshot)."""
        # Note: This is a sync method, so it returns the last known state
        # For real-time state, use the async state_manager methods
        try:
            # If there's a running loop, don't attempt to await; return a shallow copy
            asyncio.get_running_loop()
            return getattr(self.state_manager, '_state', {}).copy()
        except RuntimeError:
            # No running loop: it's safe to synchronously run the coroutine to get a snapshot
            try:
                return asyncio.run(self.state_manager.get_state_snapshot())
            except RuntimeError:
                # Fallback for environments where asyncio.run isn't allowed (rare)
                loop = asyncio.new_event_loop()
                try:
                    return loop.run_until_complete(self.state_manager.get_state_snapshot())
                finally:
                    loop.close()

    async def get_current_state_async(self) -> Dict[str, Any]:
        """Get current execution state asynchronously."""
        return await self.state_manager.get_state_snapshot()