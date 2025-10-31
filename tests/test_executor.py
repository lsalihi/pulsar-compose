import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from models.workflow import Workflow, Agent, AgentStep, ConditionalStep
from engine.executor import PulsarEngine
from engine.results import ExecutionResult, StepResult
from agents import PulsarConfig, AgentFactory

class TestPulsarEngine:
    @pytest.fixture
    def mock_config(self):
        config = PulsarConfig()
        config.openai.api_key = "test_key"
        return config

    @pytest.fixture
    def mock_agent_factory(self, mock_config):
        factory = AgentFactory(mock_config)
        # Mock the agent
        mock_agent = AsyncMock()
        mock_result = MagicMock()
        mock_result.output = "Agent response"
        mock_result.usage = {"tokens": 100}
        mock_result.cost = 0.01
        mock_result.model = "gpt-4"
        mock_agent.execute.return_value = mock_result
        factory._agents = {"openai": mock_agent}
        return factory

    @pytest.fixture
    def sample_workflow(self):
        agent = Agent(model="gpt-4", provider="openai", prompt="Test prompt")
        step = AgentStep(type="agent", step="test_step", agent="test_agent")
        workflow = Workflow(
            name="Test Workflow",
            agents={"test_agent": agent},
            workflow=[step]
        )
        return workflow

    @pytest.mark.asyncio
    async def test_basic_execution(self, sample_workflow, mock_config, mock_agent_factory):
        engine = PulsarEngine(sample_workflow, mock_config)
        engine.agent_factory = mock_agent_factory

        result = await engine.execute("test input")

        assert isinstance(result, ExecutionResult)
        assert result.workflow_name == "Test Workflow"
        assert result.success
        assert len(result.step_results) == 1
        assert result.step_results[0].success
        assert result.final_state["input"] == "test input"
        assert "test_step" in result.final_state

    @pytest.mark.asyncio
    async def test_conditional_execution_then_branch(self, mock_config, mock_agent_factory):
        # Create workflow with conditional
        agent = Agent(model="gpt-4", provider="openai", prompt="Test")
        agent_step = AgentStep(type="agent", step="agent_step", agent="test_agent")
        conditional_step = ConditionalStep(
            type="conditional",
            step="condition_step",
            **{"if": "True"},
            then=[agent_step],
            else_=[]
        )
        workflow = Workflow(
            name="Conditional Test",
            agents={"test_agent": agent},
            workflow=[conditional_step]
        )

        engine = PulsarEngine(workflow, mock_config)
        engine.agent_factory = mock_agent_factory

        result = await engine.execute()

        assert result.success
        assert len(result.step_results) == 1  # condition step with branch execution
        assert result.step_results[0].step_name == "condition_step"
        # Check that the agent step was executed in the branch
        assert "branch_results" in result.step_results[0].metadata
        assert len(result.step_results[0].metadata["branch_results"]) == 1
        assert result.step_results[0].metadata["branch_results"][0]["step_name"] == "agent_step"

    @pytest.mark.asyncio
    async def test_conditional_execution_else_branch(self, mock_config, mock_agent_factory):
        # Create workflow with conditional that evaluates to False
        agent = Agent(model="gpt-4", provider="openai", prompt="Test")
        agent_step = AgentStep(type="agent", step="agent_step", agent="test_agent")
        conditional_step = ConditionalStep(
            type="conditional",
            step="condition_step",
            **{"if": "False"},
            then=[],
            else_=[agent_step]
        )
        workflow = Workflow(
            name="Conditional Test",
            agents={"test_agent": agent},
            workflow=[conditional_step]
        )

        engine = PulsarEngine(workflow, mock_config)
        engine.agent_factory = mock_agent_factory

        result = await engine.execute()

        assert result.success
        assert len(result.step_results) == 1  # condition step with branch execution
        assert result.step_results[0].step_name == "condition_step"
        # Check that the agent step was executed in the else branch
        assert "branch_results" in result.step_results[0].metadata
        assert len(result.step_results[0].metadata["branch_results"]) == 1
        assert result.step_results[0].metadata["branch_results"][0]["step_name"] == "agent_step"

    @pytest.mark.asyncio
    async def test_execution_with_failure(self, sample_workflow, mock_config, mock_agent_factory):
        # Make agent fail
        mock_agent_factory._agents["openai"].execute.side_effect = RuntimeError("Agent failed")

        engine = PulsarEngine(sample_workflow, mock_config)
        engine.agent_factory = mock_agent_factory

        result = await engine.execute()

        assert not result.success
        assert len(result.step_results) == 1
        assert not result.step_results[0].success
        assert "Agent failed" in result.step_results[0].error

    @pytest.mark.asyncio
    async def test_template_rendering(self, mock_config, mock_agent_factory):
        # Create workflow with template
        agent = Agent(model="gpt-4", provider="openai", prompt="Hello {{user.name}}")
        step = AgentStep(type="agent", step="greeting", agent="test_agent")
        workflow = Workflow(
            name="Template Test",
            agents={"test_agent": agent},
            workflow=[step]
        )

        engine = PulsarEngine(workflow, mock_config)
        engine.agent_factory = mock_agent_factory

        # Set state with template variable
        await engine.state_manager.set("user.name", "Alice")

        result = await engine.execute()

        assert result.success
        # Verify the agent was called with rendered prompt
        call_args = mock_agent_factory._agents["openai"].execute.call_args
        assert "Hello Alice" in call_args[1]["prompt"]

    def test_get_current_state_sync(self, sample_workflow, mock_config):
        engine = PulsarEngine(sample_workflow, mock_config)
        # Initialize state first
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(engine.execute("test input"))
        finally:
            loop.close()
        
        state = engine.get_current_state()
        assert isinstance(state, dict)
        assert "input" in state

    @pytest.mark.asyncio
    async def test_complex_workflow(self, mock_config, mock_agent_factory):
        # Create a more complex workflow
        agent1 = Agent(model="gpt-4", provider="openai", prompt="Generate idea for {{input}}")
        agent2 = Agent(model="gpt-4", provider="openai", prompt="Expand on: {{idea}}")

        step1 = AgentStep(type="agent", step="generate_idea", agent="agent1", save_to="idea")
        step2 = AgentStep(type="agent", step="expand_idea", agent="agent2")

        conditional = ConditionalStep(
            type="conditional",
            step="check_quality",
            **{"if": "length(idea) > 10"},
            then=[step2],
            else_=[]
        )

        workflow = Workflow(
            name="Complex Workflow",
            agents={"agent1": agent1, "agent2": agent2},
            workflow=[step1, conditional]
        )

        engine = PulsarEngine(workflow, mock_config)
        engine.agent_factory = mock_agent_factory

        result = await engine.execute("AI development")

        assert result.success
        assert len(result.step_results) == 2  # generate + condition (with branch)
        assert result.final_state["input"] == "AI development"