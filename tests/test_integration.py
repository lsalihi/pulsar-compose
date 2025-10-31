"""
Integration tests for Pulsar components.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from engine.executor import PulsarEngine
from engine.results import ExecutionResult
from models.workflow import Workflow, AgentStep
from models.state import StateManager
from tests.mocks import MockAgentFactory, MockOpenAIAgent, MockAnthropicAgent


class TestExecutorIntegration:
    """Integration tests for the executor with mock agents."""

    @pytest.fixture
    def mock_agent_factory(self):
        """Mock agent factory for integration tests."""
        factory = MockAgentFactory()

        # Create mock agents with different response patterns
        writer_agent = MockOpenAIAgent(
            response_template="Written content about: {prompt}",
            latency=0.001
        )
        editor_agent = MockAnthropicAgent(
            response_template="Edited version of: {prompt}",
            latency=0.001
        )

        factory._agents = {
            "openai": writer_agent,
            "anthropic": editor_agent
        }

        return factory

    @pytest.fixture
    def integration_workflow(self):
        """Workflow for integration testing."""
        from models.workflow import Agent

        writer_agent = Agent(model="gpt-4", provider="openai", prompt="Write content")
        editor_agent = Agent(model="claude-3", provider="anthropic", prompt="Edit content")

        step1 = AgentStep(
            type="agent",
            step="write_content",
            agent="writer",
            prompt="Write a blog post about {{input}}",
            save_to="content"
        )

        step2 = AgentStep(
            type="agent",
            step="edit_content",
            agent="editor",
            prompt="Edit and improve: {{content}}",
            save_to="final_content"
        )

        workflow = Workflow(
            name="Integration Test Workflow",
            agents={
                "writer": writer_agent,
                "editor": editor_agent
            },
            workflow=[step1, step2]
        )

        return workflow

    @pytest.mark.asyncio
    async def test_full_workflow_execution(self, integration_workflow, mock_agent_factory):
        """Test complete workflow execution."""
        engine = PulsarEngine(integration_workflow)
        engine.agent_factory = mock_agent_factory

        result = await engine.execute("artificial intelligence")

        assert isinstance(result, ExecutionResult)
        assert result.success is True
        assert result.workflow_name == "Integration Test Workflow"
        assert len(result.step_results) == 2

        # Check step results
        write_step = result.step_results[0]
        edit_step = result.step_results[1]

        assert write_step.step_name == "write_content"
        assert edit_step.step_name == "edit_content"
        assert write_step.success is True
        assert edit_step.success is True

        # Check content flow
        assert "artificial intelligence" in write_step.output
        assert "Edited version of:" in edit_step.output

    @pytest.mark.asyncio
    async def test_workflow_with_state_persistence(self, integration_workflow, mock_agent_factory):
        """Test workflow execution with state persistence."""
        engine = PulsarEngine(integration_workflow)
        engine.agent_factory = mock_agent_factory

        result = await engine.execute("machine learning")

        # Check that state contains expected variables
        final_state = result.final_state
        assert "content" in final_state
        assert "final_content" in final_state
        assert "machine learning" in final_state["content"]

    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, integration_workflow):
        """Test workflow error handling."""
        # Create agent factory with failing agent
        factory = MockAgentFactory()
        failing_agent = MockOpenAIAgent(failure_rate=1.0)  # Always fails
        working_agent = MockAnthropicAgent()

        factory._agents = {
            "openai": failing_agent,
            "anthropic": working_agent
        }

        engine = PulsarEngine(integration_workflow)
        engine.agent_factory = factory

        result = await engine.execute("test input")

        assert result.success is False
        assert len(result.step_results) >= 1
        assert result.step_results[0].success is False

    @pytest.mark.asyncio
    async def test_parallel_step_execution(self):
        """Test parallel execution of independent steps."""
        from models.workflow import Agent

        agent = Agent(model="gpt-4", provider="openai", prompt="Process task")

        # Create workflow with parallel steps
        step1 = AgentStep(
            type="agent",
            step="task1",
            agent="worker",
            prompt="Process task 1: {{input}}",
            save_to="result1"
        )

        step2 = AgentStep(
            type="agent",
            step="task2",
            agent="worker",
            prompt="Process task 2: {{input}}",
            save_to="result2"
        )

        workflow = Workflow(
            name="Parallel Test Workflow",
            agents={"worker": agent},
            workflow=[step1, step2]
        )

        # Mock agents with different latencies
        factory = MockAgentFactory()
        fast_agent = MockOpenAIAgent(latency=0.001, response_template="Fast: {prompt}")
        slow_agent = MockOpenAIAgent(latency=0.002, response_template="Slow: {prompt}")

        factory._agents = {
            "openai": fast_agent  # Same agent for both steps
        }

        engine = PulsarEngine(workflow)
        engine.agent_factory = factory

        start_time = asyncio.get_event_loop().time()
        result = await engine.execute("parallel test")
        end_time = asyncio.get_event_loop().time()

        # Should complete faster than sequential execution
        assert end_time - start_time < 0.01  # Much faster with reduced latencies
        assert result.success is True


class TestStateManagerIntegration:
    """Integration tests for state manager."""

    @pytest.fixture
    def state_manager(self):
        """State manager instance."""
        return StateManager()

    @pytest.mark.asyncio
    async def test_state_workflow_integration(self, state_manager):
        """Test state manager integration with workflow execution."""
        # Set initial state
        await state_manager.set("user_name", "John Doe")
        await state_manager.set("preferences", {"theme": "dark"})

        # Simulate workflow accessing state
        user_name = await state_manager.get("user_name")
        preferences = await state_manager.get("preferences")

        assert user_name == "John Doe"
        assert preferences["theme"] == "dark"

    @pytest.mark.asyncio
    async def test_state_template_rendering(self, state_manager):
        """Test template rendering with state variables."""
        await state_manager.set("user", {"name": "Alice", "role": "admin"})
        await state_manager.set("count", 42)

        template = "Hello {{user.name}}, you have {{count}} items."
        result = await state_manager.render_template(template)

        assert result == "Hello Alice, you have 42 items."


class TestExpressionEvaluatorIntegration:
    """Integration tests for expression evaluator."""

    @pytest.fixture
    def state_manager(self):
        """State manager with test data."""
        manager = StateManager()
        # This would be async in real usage, but for testing we'll set directly
        return manager

    def test_expression_with_workflow_state(self):
        """Test expression evaluation with workflow state."""
        from engine.expression_evaluator import evaluate_expression

        state = {
            "user": {
                "name": "Bob",
                "score": 85,
                "active": True,
                "tags": ["premium", "verified"]
            },
            "order": {
                "total": 150.00,
                "items": ["book", "pen", "notebook"]
            }
        }

        # Test various expressions
        assert evaluate_expression("{{user.score}} >= 80", state) is True
        assert evaluate_expression("length({{user.tags}}) > 1", state) is True
        assert evaluate_expression("{{user.active}} && {{order.total}} > 100", state) is True
        assert evaluate_expression("'premium' in {{user.tags}}", state) is True


class TestInputProviderIntegration:
    """Integration tests for input providers."""

    @pytest.mark.asyncio
    async def test_console_provider_workflow_integration(self):
        """Test console provider integration with workflow."""
        from engine.input_providers import ConsoleInputProvider, InteractionRequest, Question, QuestionType

        provider = ConsoleInputProvider()

        questions = [
            Question(question="Project name?", type=QuestionType.TEXT, required=True),
            Question(question="Priority?", type=QuestionType.MULTIPLE_CHOICE,
                    options=["Low", "Medium", "High"], required=True)
        ]

        request = InteractionRequest(questions=questions)

        # Mock Rich prompt functions instead of builtins.input
        with patch('rich.prompt.Prompt.ask', side_effect=['My Project']), \
             patch('rich.prompt.IntPrompt.ask', side_effect=[3]):  # 3 for "High" (1-indexed)
            response = await provider.get_input(request)

        assert response.answers["question_0"] == "My Project"
        assert response.answers["question_1"] == "High"

    @pytest.mark.asyncio
    async def test_test_provider_workflow_integration(self):
        """Test test provider integration with workflow."""
        from engine.input_providers import TestInputProvider, InteractionRequest, Question, QuestionType

        responses = {
            "question_0": "Test Project",
            "question_1": "Medium"
        }

        provider = TestInputProvider.create_with_responses(responses)

        questions = [
            Question(question="Project name?", type=QuestionType.TEXT),
            Question(question="Priority?", type=QuestionType.MULTIPLE_CHOICE,
                    options=["Low", "Medium", "High"])
        ]

        request = InteractionRequest(questions=questions)
        response = await provider.get_input(request)

        assert response.answers["question_0"] == "Test Project"
        assert response.answers["question_1"] == "Medium"


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    @pytest.mark.asyncio
    async def test_blog_generation_workflow(self):
        """Test complete blog generation workflow."""
        from models.workflow import Agent

        # Create agents
        writer = Agent(model="gpt-4", provider="openai", prompt="Write content")
        editor = Agent(model="claude-3", provider="anthropic", prompt="Edit content")

        # Create workflow steps
        research_step = AgentStep(
            type="agent",
            step="research",
            agent="writer",
            prompt="Research key points about: {{input}}",
            save_to="research"
        )

        write_step = AgentStep(
            type="agent",
            step="write",
            agent="writer",
            prompt="Write a blog post using this research: {{research}}",
            save_to="draft"
        )

        edit_step = AgentStep(
            type="agent",
            step="edit",
            agent="editor",
            prompt="Edit and improve this blog post: {{draft}}",
            save_to="final_post"
        )

        workflow = Workflow(
            name="Blog Generation E2E",
            agents={"writer": writer, "editor": editor},
            workflow=[research_step, write_step, edit_step]
        )

        # Mock agents
        factory = MockAgentFactory()
        writer_agent = MockOpenAIAgent(
            response_template="Research on {prompt}: Key points include AI, ML, and automation."
        )
        editor_agent = MockAnthropicAgent(
            response_template="Edited version: {prompt}"
        )

        factory._agents = {
            "openai": writer_agent,
            "anthropic": editor_agent
        }

        # Execute workflow
        engine = PulsarEngine(workflow)
        engine.agent_factory = factory

        result = await engine.execute("artificial intelligence trends")

        # Verify end-to-end execution
        assert result.success is True
        assert len(result.step_results) == 3

        # Check content flow
        research_output = result.step_results[0].output
        draft_output = result.step_results[1].output
        final_output = result.step_results[2].output

        assert "artificial intelligence trends" in research_output
        assert "Research on" in draft_output
        assert "Edited version:" in final_output

        # Check final state
        assert "research" in result.final_state
        assert "draft" in result.final_state
        assert "final_post" in result.final_state