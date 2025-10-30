import asyncio
from typing import TYPE_CHECKING, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from engine.step_handlers.base import BaseStepHandler

if TYPE_CHECKING:
    from models.state import StateManager
    from models.workflow import AgentStep, Agent
    from agents import AgentFactory

class AgentStepHandler(BaseStepHandler):
    """Handler for executing agent steps."""

    def __init__(self, state_manager: "StateManager", agent_factory: "AgentFactory", agents: Dict[str, "Agent"]):
        super().__init__(state_manager)
        self.agent_factory = agent_factory
        self.agents = agents

    async def can_handle(self, step) -> bool:
        """Check if step is an agent step."""
        return hasattr(step, 'type') and step.type == "agent"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((RuntimeError, asyncio.TimeoutError))
    )
    async def execute(self, step: "AgentStep") -> "StepResult":
        """Execute an agent step."""
        try:
            # Get agent configuration
            if step.agent not in self.agents:
                raise ValueError(f"Agent '{step.agent}' not found in workflow agents")

            agent_config = self.agents[step.agent]

            # Render prompt with current state
            if step.prompt:
                prompt = await self.state_manager.render_template(step.prompt)
            else:
                prompt = await self.state_manager.render_template(agent_config.prompt)

            # Render context if present
            context = None
            if step.context:
                context = await self.state_manager.render_template(step.context)

            # Get agent and execute
            agent = self.agent_factory.get_agent(agent_config.provider, step.agent)
            result = await agent.execute(
                prompt=prompt,
                model=agent_config.model,
                **agent_config.parameters
            )

            # Update state with output
            if step.save_to:
                await self.state_manager.set(step.save_to, result.output)
            else:
                # Default save to step name
                await self.state_manager.set(step.step, result.output)

            # Update execution history
            await self.state_manager.update_from_agent_output(step.step, result.output)

            metadata = {
                "agent_provider": agent_config.provider,
                "model": result.model,
                "usage": result.usage,
                "cost": result.cost,
                "retries": 0  # Will be set by retry decorator
            }

            return await self._create_step_result(
                step_name=step.step,
                success=True,
                output=result.output,
                metadata=metadata
            )

        except Exception as e:
            error_msg = f"Agent execution failed: {str(e)}"
            return await self._create_step_result(
                step_name=step.step,
                success=False,
                error=error_msg,
                metadata={"exception_type": type(e).__name__}
            )