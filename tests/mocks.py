"""
Mock providers for testing Pulsar components.
"""

import asyncio
import time
import random
from typing import Dict, Any, Optional, List
from unittest.mock import AsyncMock, MagicMock

from agents.base import BaseAgent, AgentResult, AgentConfig


class MockOpenAIAgent(BaseAgent):
    """Mock OpenAI agent for testing."""

    def __init__(self,
                 response_template: Optional[str] = None,
                 latency: float = 0.001,
                 failure_rate: float = 0.0):
        # Create a mock config
        config = AgentConfig(provider="openai", api_key="mock-key")
        self.config = config
        self.response_template = response_template or "Mock OpenAI response to: {prompt}"
        self.latency = latency
        self.failure_rate = failure_rate
        self.call_history: List[Dict[str, Any]] = []

    async def execute(self, prompt: str, model: str, **parameters) -> AgentResult:
        """Mock OpenAI execution."""
        self.call_history.append({
            "prompt": prompt,
            "model": model,
            "parameters": parameters,
            "timestamp": time.time()
        })

        # Simulate latency
        if self.latency > 0:
            await asyncio.sleep(self.latency)

        # Simulate failures
        if random.random() < self.failure_rate:
            raise Exception("Mock OpenAI API error")

        # Generate response
        output = self.response_template.format(prompt=prompt)

        return AgentResult(
            output=output,
            usage={
                "prompt_tokens": len(prompt.split()) * 2,
                "completion_tokens": len(output.split()) * 2,
                "total_tokens": (len(prompt.split()) + len(output.split())) * 2
            },
            model=model,
            metadata={"provider": "openai", "mock": True},
            cost=self.estimate_cost({
                "prompt_tokens": len(prompt.split()) * 2,
                "completion_tokens": len(output.split()) * 2
            }, model)
        )

    def estimate_cost(self, usage: Dict[str, int], model: str) -> float:
        """Mock cost estimation."""
        return 0.01  # Fixed mock cost


class MockAnthropicAgent(BaseAgent):
    """Mock Anthropic agent for testing."""

    def __init__(self,
                 response_template: Optional[str] = None,
                 latency: float = 0.001,
                 failure_rate: float = 0.0):
        # Create a mock config
        config = AgentConfig(provider="anthropic", api_key="mock-key")
        self.config = config
        self.response_template = response_template or "Mock Claude response to: {prompt}"
        self.latency = latency
        self.failure_rate = failure_rate
        self.call_history: List[Dict[str, Any]] = []

    async def execute(self, prompt: str, model: str, **parameters) -> AgentResult:
        """Mock Anthropic execution."""
        self.call_history.append({
            "prompt": prompt,
            "model": model,
            "parameters": parameters,
            "timestamp": time.time()
        })

        # Simulate latency
        if self.latency > 0:
            await asyncio.sleep(self.latency)

        # Simulate failures
        if random.random() < self.failure_rate:
            raise Exception("Mock Anthropic API error")

        # Generate response
        output = self.response_template.format(prompt=prompt)

        return AgentResult(
            output=output,
            usage={
                "prompt_tokens": len(prompt.split()) * 2,
                "completion_tokens": len(output.split()) * 2,
                "total_tokens": (len(prompt.split()) + len(output.split())) * 2
            },
            model=model,
            metadata={"provider": "anthropic", "mock": True},
            cost=self.estimate_cost({
                "prompt_tokens": len(prompt.split()) * 2,
                "completion_tokens": len(output.split()) * 2
            }, model)
        )

    def estimate_cost(self, usage: Dict[str, int], model: str) -> float:
        """Mock cost estimation."""
        return 0.015  # Fixed mock cost


class MockLocalAgent(BaseAgent):
    """Mock local agent for testing."""

    def __init__(self,
                 response_template: Optional[str] = None,
                 latency: float = 0.001,
                 failure_rate: float = 0.0):
        # Create a mock config
        config = AgentConfig(provider="local", base_url="http://localhost:11434")
        self.config = config
        self.response_template = response_template or "Mock local response to: {prompt}"
        self.latency = latency
        self.failure_rate = failure_rate
        self.call_history: List[Dict[str, Any]] = []

    async def execute(self, prompt: str, model: str, **parameters) -> AgentResult:
        """Mock local execution."""
        self.call_history.append({
            "prompt": prompt,
            "model": model,
            "parameters": parameters,
            "timestamp": time.time()
        })

        # Simulate latency
        if self.latency > 0:
            await asyncio.sleep(self.latency)

        # Simulate failures
        if random.random() < self.failure_rate:
            raise Exception("Mock local API error")

        # Generate response
        output = self.response_template.format(prompt=prompt)

        return AgentResult(
            output=output,
            usage={
                "prompt_tokens": len(prompt.split()) * 2,
                "completion_tokens": len(output.split()) * 2,
                "total_tokens": (len(prompt.split()) + len(output.split())) * 2
            },
            model=model,
            metadata={"provider": "local", "mock": True},
            cost=0.0  # Local models are free
        )

    def estimate_cost(self, usage: Dict[str, int], model: str) -> float:
        """Mock cost estimation - local models are free."""
        return 0.0


class MockAgentFactory:
    """Mock agent factory for testing."""

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def get_agent(self, provider: str, agent_name: Optional[str] = None) -> BaseAgent:
        """Get or create a mock agent."""
        # First check if we have a named agent
        if agent_name and agent_name in self._agents:
            return self._agents[agent_name]
        
        # Then check if we have a provider-specific agent
        if provider in self._agents:
            return self._agents[provider]
        
        # Otherwise create based on provider type
        if provider == "openai":
            self._agents[provider] = MockOpenAIAgent()
        elif provider == "anthropic":
            self._agents[provider] = MockAnthropicAgent()
        elif provider == "local":
            self._agents[provider] = MockLocalAgent()
        else:
            raise ValueError(f"Unknown provider: {provider}")
        return self._agents[provider]

    def add_agent(self, name: str, agent: BaseAgent):
        """Add a custom agent to the factory."""
        self._agents[name] = agent


class TestInputProvider:
    """Mock input provider for testing."""

    def __init__(self, responses: Optional[Dict[str, Any]] = None):
        self.responses = responses or {}
        self.call_count = 0

    @classmethod
    def create_with_responses(cls, responses: Dict[str, Any]) -> "TestInputProvider":
        """Create provider with predefined responses."""
        return cls(responses)

    async def get_input(self, request):
        """Mock input retrieval."""
        self.call_count += 1

        # Mock interaction response
        from engine.input_providers.base import InteractionResponse, Answer

        answers = {}
        for question in request.questions:
            answer_value = self.responses.get(question.id, f"Mock answer for {question.question}")
            answers[question.id] = answer_value

        return InteractionResponse(answers=answers)


class MockWorkflowEngine:
    """Mock workflow engine for testing."""

    def __init__(self, success_rate: float = 1.0, latency: float = 0.001):
        self.success_rate = success_rate
        self.latency = latency
        self.execution_count = 0
        self.execution_history: List[Dict[str, Any]] = []

    async def execute(self, input_data: Any) -> Dict[str, Any]:
        """Mock workflow execution."""
        self.execution_count += 1

        # Simulate latency
        if self.latency > 0:
            await asyncio.sleep(self.latency)

        # Record execution
        execution_record = {
            "input": input_data,
            "timestamp": time.time(),
            "execution_id": self.execution_count
        }
        self.execution_history.append(execution_record)

        # Simulate success/failure
        if random.random() < self.success_rate:
            return {
                "success": True,
                "output": f"Processed: {input_data}",
                "execution_id": self.execution_count
            }
        else:
            raise Exception(f"Mock workflow failure for input: {input_data}")

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            "total_executions": self.execution_count,
            "success_rate": self.success_rate,
            "average_latency": self.latency
        }


class MockStateManager:
    """Mock state manager for testing."""

    def __init__(self):
        self.state: Dict[str, Any] = {}
        self.operation_count = 0

    async def get(self, key: str) -> Any:
        """Get value from state."""
        self.operation_count += 1
        return self.state.get(key)

    async def set(self, key: str, value: Any):
        """Set value in state."""
        self.operation_count += 1
        self.state[key] = value

    async def delete(self, key: str):
        """Delete value from state."""
        self.operation_count += 1
        if key in self.state:
            del self.state[key]

    def clear(self):
        """Clear all state."""
        self.state.clear()
        self.operation_count += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get state statistics."""
        return {
            "keys_count": len(self.state),
            "operations": self.operation_count
        }


class MockExpressionEvaluator:
    """Mock expression evaluator for testing."""

    def __init__(self, mock_results: Optional[Dict[str, Any]] = None):
        self.mock_results = mock_results or {}
        self.evaluation_count = 0

    def evaluate_expression(self, expression: str, context: Dict[str, Any]) -> Any:
        """Mock expression evaluation."""
        self.evaluation_count += 1

        # Check if we have a mock result
        if expression in self.mock_results:
            return self.mock_results[expression]

        # Simple mock evaluation logic
        if "length(" in expression:
            return len(context.get("test_list", []))
        elif ">" in expression:
            parts = expression.split(">")
            if len(parts) == 2:
                left = int(parts[0].strip())
                right = int(parts[1].strip())
                return left > right
        elif "&&" in expression:
            return True  # Mock as true for testing

        return True  # Default to true for most tests