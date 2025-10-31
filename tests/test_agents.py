"""
Unit tests for Pulsar agents.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any

from agents.base import BaseAgent, AgentResult, AgentConfig
from agents.openai_agent import OpenAIAgent
from agents.anthropic_agent import AnthropicAgent
from agents.local_agent import LocalAgent
from agents.factory import AgentFactory
from agents.config import PulsarConfig, ProviderConfig
from tests.mocks import MockOpenAIAgent, MockAnthropicAgent, MockLocalAgent


class TestBaseAgent:
    """Test the abstract BaseAgent class."""

    def test_base_agent_is_abstract(self):
        """Test that BaseAgent cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAgent()

    def test_agent_result_creation(self):
        """Test creating AgentResult instances."""
        result = AgentResult(
            output="Test output",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            model="gpt-4",
            metadata={"test": "data"},
            cost=0.002
        )

        assert result.output == "Test output"
        assert result.usage["total_tokens"] == 30
        assert result.model == "gpt-4"
        assert result.metadata["test"] == "data"
        assert result.cost == 0.002


class TestOpenAIAgent:
    """Test OpenAI agent implementation."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return PulsarConfig(
            openai=ProviderConfig(
                api_key="test-key",
                timeout=30,
                max_retries=2
            )
        )

    @pytest.fixture
    def agent_config(self, config):
        """Create agent configuration."""
        return AgentConfig(
            provider="openai",
            api_key=config.openai.api_key,
            timeout=config.openai.timeout,
            max_retries=config.openai.max_retries
        )

    @pytest.fixture
    def openai_agent(self, agent_config):
        """Create OpenAI agent instance."""
        return OpenAIAgent(agent_config)

    @pytest.mark.asyncio
    async def test_execute_success(self, openai_agent):
        """Test successful OpenAI execution."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30

        with patch.object(openai_agent.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response

            result = await openai_agent.execute("Test prompt", "gpt-4")

            assert isinstance(result, AgentResult)
            assert result.output == "Test response"
            assert result.usage["total_tokens"] == 30
            assert result.model == "gpt-4"
            assert result.metadata["provider"] == "openai"
            assert result.cost > 0

    @pytest.mark.asyncio
    async def test_execute_with_parameters(self, openai_agent):
        """Test execution with custom parameters."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Custom response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 15
        mock_response.usage.completion_tokens = 25
        mock_response.usage.total_tokens = 40

        with patch.object(openai_agent.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response

            result = await openai_agent.execute(
                "Test prompt",
                "gpt-4",
                temperature=0.5,
                max_tokens=100
            )

            assert result.output == "Custom response"
            mock_create.assert_called_once()
            call_args = mock_create.call_args[1]
            assert call_args["temperature"] == 0.5
            assert call_args["max_tokens"] == 100

    @pytest.mark.asyncio
    async def test_execute_api_error(self, openai_agent):
        """Test handling of OpenAI API errors."""
        from openai import OpenAIError

        with patch.object(openai_agent.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = OpenAIError("API Error")

            with pytest.raises(RuntimeError, match="OpenAI API error"):
                await openai_agent.execute("Test prompt", "gpt-4")

    def test_cost_calculation(self, openai_agent):
        """Test cost estimation for different models."""
        # Test GPT-4 pricing
        usage = {"prompt_tokens": 1000, "completion_tokens": 1000, "total_tokens": 2000}
        cost = openai_agent.estimate_cost(usage, "gpt-4")
        expected_cost = (1000/1000 * 0.03) + (1000/1000 * 0.06)  # 0.03 + 0.06 = 0.09
        assert abs(cost - expected_cost) < 0.001

        # Test GPT-3.5 pricing
        cost_35 = openai_agent.estimate_cost(usage, "gpt-3.5-turbo")
        expected_cost_35 = (1000/1000 * 0.0015) + (1000/1000 * 0.002)  # 0.0015 + 0.002 = 0.0035
        assert abs(cost_35 - expected_cost_35) < 0.001

        # Test unknown model
        cost_unknown = openai_agent.estimate_cost(usage, "unknown-model")
        assert cost_unknown == 0.0


class TestAnthropicAgent:
    """Test Anthropic agent implementation."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return PulsarConfig(
            anthropic=ProviderConfig(
                api_key="test-anthropic-key",
                timeout=30,
                max_retries=2
            )
        )

    @pytest.fixture
    def agent_config(self, config):
        """Create agent configuration."""
        return AgentConfig(
            provider="anthropic",
            api_key=config.anthropic.api_key,
            timeout=config.anthropic.timeout,
            max_retries=config.anthropic.max_retries
        )

    @pytest.fixture
    def anthropic_agent(self, agent_config):
        """Create Anthropic agent instance."""
        return AnthropicAgent(agent_config)

    @pytest.mark.asyncio
    async def test_execute_success(self, anthropic_agent):
        """Test successful Anthropic execution."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Claude response"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock()
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 20

        with patch.object(anthropic_agent.client.messages, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response

            result = await anthropic_agent.execute("Test prompt", "claude-3")

            assert isinstance(result, AgentResult)
            assert result.output == "Claude response"
            assert result.usage["input_tokens"] == 10
            assert result.usage["output_tokens"] == 20
            assert result.model == "claude-3"
            assert result.metadata["provider"] == "anthropic"

    @pytest.mark.asyncio
    async def test_execute_with_system_prompt(self, anthropic_agent):
        """Test execution with system prompt."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "System-aware response"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock()
        mock_response.usage.input_tokens = 15
        mock_response.usage.output_tokens = 25

        with patch.object(anthropic_agent.client.messages, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response

            result = await anthropic_agent.execute(
                "Test prompt",
                "claude-3",
                system="You are a helpful assistant."
            )

            assert result.output == "System-aware response"
            mock_create.assert_called_once()
            call_args = mock_create.call_args[1]
            assert "messages" in call_args  # messages API uses 'messages' instead of 'prompt'


class TestLocalAgent:
    """Test local agent implementation."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return PulsarConfig(
            local=ProviderConfig(
                base_url="http://localhost:11434",
                timeout=30,
                max_retries=2
            )
        )

    @pytest.fixture
    def agent_config(self, config):
        """Create agent configuration."""
        return AgentConfig(
            provider="local",
            base_url=config.local.base_url,
            timeout=config.local.timeout,
            max_retries=config.local.max_retries
        )

    @pytest.fixture
    def local_agent(self, agent_config):
        """Create local agent instance."""
        return LocalAgent(agent_config)

    @pytest.mark.asyncio
    async def test_execute_success(self, local_agent):
        """Test successful local execution."""
        from unittest.mock import AsyncMock, MagicMock

        class MockResponse:
            def __init__(self):
                self.status = 200
                self.json = AsyncMock(return_value={
                    "response": "Local model response",
                    "done": True,
                    "prompt_eval_count": 10,
                    "eval_count": 20
                })

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        mock_response = MockResponse()

        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            result = await local_agent.execute("Test prompt", "llama2")

            assert isinstance(result, AgentResult)
            assert result.output == "Local model response"
            assert result.usage["prompt_tokens"] == 10
            assert result.usage["completion_tokens"] == 20
            assert result.model == "llama2"
            assert result.metadata["provider"] == "local"

    @pytest.mark.asyncio
    async def test_execute_pipeline_error(self, local_agent):
        """Test handling of pipeline errors."""
        from unittest.mock import AsyncMock, MagicMock

        class MockResponse:
            def __init__(self):
                self.status = 500
                self.text = AsyncMock(return_value="Internal server error")

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        mock_response = MockResponse()

        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            with pytest.raises(RuntimeError, match="Ollama API error"):
                await local_agent.execute("Test prompt", "llama2")


class TestMockAgents:
    """Test mock agent implementations."""

    def test_mock_openai_execute(self):
        """Test MockOpenAI agent execution."""
        agent = MockOpenAIAgent()
        result = asyncio.run(agent.execute("Test prompt", "gpt-4"))

        assert isinstance(result, AgentResult)
        assert "Test prompt" in result.output
        assert result.model == "gpt-4"

    def test_mock_anthropic_execute(self):
        """Test MockAnthropic agent execution."""
        agent = MockAnthropicAgent()
        result = asyncio.run(agent.execute("Test prompt", "claude-3"))

        assert isinstance(result, AgentResult)
        assert "Test prompt" in result.output
        assert result.model == "claude-3"

    def test_mock_agent_failure_simulation(self):
        """Test mock agent failure simulation."""
        agent = MockOpenAIAgent(failure_rate=1.0)  # Always fail

        with pytest.raises(Exception):  # Should raise an exception
            asyncio.run(agent.execute("Test prompt", "gpt-4"))

    def test_mock_agent_latency(self):
        """Test mock agent latency simulation."""
        import time
        agent = MockOpenAIAgent(latency=0.2)

        start_time = time.time()
        result = asyncio.run(agent.execute("Test prompt", "gpt-4"))
        execution_time = time.time() - start_time

        assert execution_time >= 0.2  # Should take at least the specified latency
        assert isinstance(result, AgentResult)

    def test_mock_agent_call_history(self):
        """Test mock agent call history tracking."""
        agent = MockOpenAIAgent()

        # Execute multiple times
        asyncio.run(agent.execute("Prompt 1", "gpt-4"))
        asyncio.run(agent.execute("Prompt 2", "gpt-4"))

        # Check call history
        assert len(agent.call_history) == 2
        assert agent.call_history[0]["prompt"] == "Prompt 1"
        assert agent.call_history[1]["prompt"] == "Prompt 2"


class TestAgentFactory:
    """Test agent factory functionality."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return PulsarConfig(
            openai=ProviderConfig(api_key="openai-key"),
            anthropic=ProviderConfig(api_key="anthropic-key"),
            local=ProviderConfig(base_url="http://localhost:11434")
        )

    @pytest.fixture
    def agent_factory(self, config):
        """Create agent factory instance."""
        return AgentFactory(config)

    def test_create_openai_agent(self, agent_factory):
        """Test creating OpenAI agent."""
        agent = agent_factory.get_agent("openai")
        assert isinstance(agent, OpenAIAgent)

    def test_create_anthropic_agent(self, agent_factory):
        """Test creating Anthropic agent."""
        agent = agent_factory.get_agent("anthropic")
        assert isinstance(agent, AnthropicAgent)

    def test_create_unknown_agent(self, agent_factory):
        """Test creating unknown agent type."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            agent_factory.get_agent("unknown_provider")

    def test_agent_caching(self, agent_factory):
        """Test that agents are cached properly."""
        agent1 = agent_factory.get_agent("openai")
        agent2 = agent_factory.get_agent("openai")

        # Should be the same instance (cached)
        assert agent1 is agent2

    def test_list_supported_providers(self, agent_factory):
        """Test listing supported providers."""
        providers = agent_factory.list_supported_providers()
        assert "openai" in providers
        assert "anthropic" in providers
        assert "local" in providers

    @pytest.mark.asyncio
    async def test_execute_with_agent(self, agent_factory):
        """Test convenience execution method."""
        with patch.object(agent_factory.get_agent("openai"), 'execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = AgentResult(
                output="Test result",
                usage={},
                model="gpt-4"
            )

            result = await agent_factory.execute_with_agent("openai", "Test prompt", "gpt-4")

            assert result.output == "Test result"
            mock_execute.assert_called_once_with("Test prompt", "gpt-4")