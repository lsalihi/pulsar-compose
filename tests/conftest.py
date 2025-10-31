"""
Pytest configuration and shared fixtures for Pulsar testing.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional

from agents import PulsarConfig, AgentFactory
from models.workflow import Workflow, Agent, AgentStep, ConditionalStep
from models.state import StateManager
from engine.executor import PulsarEngine
from engine.results import ExecutionResult, StepResult
from engine.input_providers import (
    InputProviderFactory,
    TestInputProvider,
    InteractionRequest,
    InteractionResponse,
    Question,
    QuestionType
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for the test session."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_config():
    """Mock Pulsar configuration for testing."""
    config = PulsarConfig()
    config.openai.api_key = "test_openai_key"
    config.anthropic.api_key = "test_anthropic_key"
    config.ollama.base_url = "http://localhost:11434"
    return config


@pytest.fixture
def mock_agent_result():
    """Mock agent execution result."""
    result = MagicMock()
    result.output = "Mock agent response"
    result.usage = {"total_tokens": 150, "prompt_tokens": 50, "completion_tokens": 100}
    result.cost = 0.002
    result.model = "gpt-4"
    result.success = True
    result.error = None
    return result


@pytest.fixture
def mock_openai_agent(mock_agent_result):
    """Mock OpenAI agent."""
    agent = AsyncMock()
    agent.execute.return_value = mock_agent_result
    agent.model = "gpt-4"
    agent.provider = "openai"
    return agent


@pytest.fixture
def mock_anthropic_agent(mock_agent_result):
    """Mock Anthropic agent."""
    agent = AsyncMock()
    agent.execute.return_value = mock_agent_result
    agent.model = "claude-3"
    agent.provider = "anthropic"
    return agent


@pytest.fixture
def mock_agent_factory(mock_openai_agent, mock_anthropic_agent, mock_config):
    """Mock agent factory with predefined agents."""
    factory = AgentFactory(mock_config)

    # Mock the agents
    factory._agents = {
        "openai": mock_openai_agent,
        "anthropic": mock_anthropic_agent,
        "gpt-4": mock_openai_agent,
        "claude-3": mock_anthropic_agent
    }

    # Mock the creation methods
    factory.create_agent = MagicMock(side_effect=lambda name, **kwargs: factory._agents.get(name))

    return factory


@pytest.fixture
def sample_workflow():
    """Sample workflow for testing."""
    agent = Agent(
        model="gpt-4",
        provider="openai",
        prompt="You are a helpful assistant.",
        parameters={"temperature": 0.7}
    )

    step1 = AgentStep(
        type="agent",
        step="content_writer",
        agent="openai",
        prompt="Write a blog post about {{input}}",
        save_to="blog_content"
    )

    step2 = AgentStep(
        type="agent",
        step="editor",
        agent="anthropic",
        prompt="Edit and improve this content: {{blog_content}}",
        save_to="edited_content"
    )

    workflow = Workflow(
        name="Test Blog Workflow",
        description="A test workflow for blog writing",
        version="1.0.0",
        agents={
            "writer": agent,
            "editor": agent
        },
        workflow=[step1, step2],
        config={
            "max_retries": 3,
            "timeout": 60
        }
    )

    return workflow


@pytest.fixture
def conditional_workflow():
    """Workflow with conditional logic for testing."""
    agent = Agent(model="gpt-4", provider="openai")

    step1 = AgentStep(
        type="agent",
        step="analyzer",
        agent="openai",
        prompt="Analyze this text: {{input}}. Rate quality from 1-10.",
        save_to="analysis"
    )

    condition = ConditionalStep(
        type="conditional",
        step="quality_check",
        if_="{{analysis | regex_match(r'(\d+)/10') | int >= 7}}",
        then_=[
            AgentStep(
                type="agent",
                step="publisher",
                agent="openai",
                prompt="Publish this high-quality content: {{analysis}}",
                save_to="published"
            )
        ],
        else_=[
            AgentStep(
                type="agent",
                step="reviser",
                agent="anthropic",
                prompt="Revise this content: {{analysis}}",
                save_to="revised"
            )
        ]
    )

    workflow = Workflow(
        name="Conditional Test Workflow",
        agents={"analyzer": agent, "publisher": agent, "reviser": agent},
        workflow=[step1, condition]
    )

    return workflow


@pytest.fixture
def interaction_workflow():
    """Workflow with user interaction for testing."""
    from models.workflow import InteractionStep

    agent = Agent(model="gpt-4", provider="openai")

    interaction_step = InteractionStep(
        type="interaction",
        step="get_preferences",
        provider="test",
        questions=[
            Question(
                question="What type of content?",
                type=QuestionType.MULTIPLE_CHOICE,
                options=["Blog", "Article", "Tutorial"],
                required=True
            ),
            Question(
                question="Target audience?",
                type=QuestionType.TEXT,
                required=True
            )
        ],
        save_to="user_prefs"
    )

    content_step = AgentStep(
        type="agent",
        step="content_generator",
        agent="openai",
        prompt="Generate {{user_prefs.question_0}} about {{user_prefs.question_1}}",
        save_to="content"
    )

    workflow = Workflow(
        name="Interaction Test Workflow",
        agents={"content_generator": agent},
        workflow=[interaction_step, content_step]
    )

    return workflow


@pytest.fixture
def mock_state_manager():
    """Mock state manager for testing."""
    state_manager = AsyncMock(spec=StateManager)

    # Mock state operations
    state_manager.set = AsyncMock()
    state_manager.get = AsyncMock(return_value={})
    state_manager.get_state_snapshot = AsyncMock(return_value={"test": "data"})

    return state_manager


@pytest.fixture
def test_input_provider():
    """Test input provider with predefined responses."""
    responses = {
        "question_0": "Blog",
        "question_1": "Developers"
    }
    return TestInputProvider.create_with_responses(responses)


@pytest.fixture
def sample_interaction_request():
    """Sample interaction request for testing."""
    questions = [
        Question(
            question="What's your name?",
            type=QuestionType.TEXT,
            required=True
        ),
        Question(
            question="Choose a framework",
            type=QuestionType.MULTIPLE_CHOICE,
            options=["React", "Vue", "Angular"],
            required=True
        ),
        Question(
            question="Experience level?",
            type=QuestionType.MULTIPLE_CHOICE,
            options=["Beginner", "Intermediate", "Advanced"],
            required=True
        )
    ]

    return InteractionRequest(
        questions=questions,
        timeout=30,
        metadata={"title": "Test Survey"}
    )


@pytest.fixture
def sample_interaction_response():
    """Sample interaction response for testing."""
    return InteractionResponse(
        answers={
            "question_0": "John Doe",
            "question_1": "React",
            "question_2": "Intermediate"
        },
        metadata={"provider": "test"}
    )


# Test utilities
class TestUtils:
    """Utility functions for tests."""

    @staticmethod
    def create_mock_agent_response(output: str = "Test response",
                                 usage: Optional[Dict[str, int]] = None,
                                 cost: float = 0.01,
                                 model: str = "gpt-4",
                                 success: bool = True):
        """Create a mock agent response."""
        result = MagicMock()
        result.output = output
        result.usage = usage or {"total_tokens": 100, "prompt_tokens": 50, "completion_tokens": 50}
        result.cost = cost
        result.model = model
        result.success = success
        result.error = None if success else "Mock error"
        return result

    @staticmethod
    def create_test_workflow_file(content: str, temp_dir: Path) -> Path:
        """Create a temporary workflow file."""
        workflow_file = temp_dir / "test_workflow.yml"
        workflow_file.write_text(content)
        return workflow_file

    @staticmethod
    def mock_openai_api():
        """Context manager to mock OpenAI API calls."""
        return patch('openai.OpenAI')

    @staticmethod
    def mock_anthropic_api():
        """Context manager to mock Anthropic API calls."""
        return patch('anthropic.Anthropic')

    @staticmethod
    async def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1):
        """Wait for a condition to become true."""
        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            if await condition_func():
                return True
            await asyncio.sleep(interval)

        return False


# Make TestUtils available as a fixture
@pytest.fixture
def test_utils():
    """Test utilities fixture."""
    return TestUtils()


# Performance testing fixtures
@pytest.fixture
def benchmark_config():
    """Configuration for performance benchmarks."""
    return {
        "warmup_rounds": 2,
        "benchmark_rounds": 5,
        "max_time": 10.0
    }


# Environment setup
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    original_env = dict(os.environ)

    # Set test environment variables
    os.environ.update({
        "PULSAR_ENV": "test",
        "OPENAI_API_KEY": "test_key",
        "ANTHROPIC_API_KEY": "test_key",
    })

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_mocks():
    """Clean up any mocks after each test."""
    yield
    # Any cleanup logic here