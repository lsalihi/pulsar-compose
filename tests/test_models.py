import pytest
import tempfile
import os
from models.workflow import Workflow, Agent, AgentStep, ConditionalStep
from models.template import TemplateRenderer

class TestWorkflowModels:
    def test_agent_creation(self):
        agent = Agent(
            model="gpt-4",
            provider="openai",
            prompt="Hello {{name}}",
            parameters={"temperature": 0.7}
        )
        assert agent.model == "gpt-4"
        assert agent.provider == "openai"
        assert agent.prompt == "Hello {{name}}"
        assert agent.parameters == {"temperature": 0.7}

    def test_agent_validation_error(self):
        with pytest.raises(ValueError):
            Agent(
                model="gpt-4",
                provider="invalid_provider",  # Invalid literal
                prompt="Hello"
            )

    def test_agent_step_creation(self):
        step = AgentStep(
            type="agent",
            step="test_step",
            agent="test_agent",
            context="Context: {{input}}",
            save_to="output",
            max_retries=5
        )
        assert step.step == "test_step"
        assert step.agent == "test_agent"
        assert step.context == "Context: {{input}}"
        assert step.save_to == "output"
        assert step.max_retries == 5

    def test_conditional_step_creation(self):
        sub_step = AgentStep(type="agent", step="sub", agent="agent1")
        step = ConditionalStep(
            type="conditional",
            step="cond_step",
            **{"if": "{{score}} > 80"},
            then=[sub_step],
            else_=[]
        )
        assert step.step == "cond_step"
        assert step.if_ == "{{score}} > 80"
        assert len(step.then) == 1
        assert step.else_ == []

    def test_workflow_creation(self):
        agent = Agent(model="gpt-4", provider="openai", prompt="Prompt")
        step = AgentStep(type="agent", step="step1", agent="agent1")
        workflow = Workflow(
            version="0.1",
            name="Test Workflow",
            agents={"agent1": agent},
            workflow=[step]
        )
        assert workflow.name == "Test Workflow"
        assert len(workflow.workflow) == 1

    def test_workflow_validation_missing_agent(self):
        step = AgentStep(type="agent", step="step1", agent="nonexistent")
        with pytest.raises(ValueError):
            Workflow(
                name="Test",
                agents={},
                workflow=[step]
            )

    def test_yaml_parsing(self):
        yaml_content = """
version: "0.1"
name: "Test Workflow"
agents:
  agent1:
    model: "gpt-4"
    provider: "openai"
    prompt: "Hello {{name}}"
workflow:
  - type: agent
    step: "step1"
    agent: "agent1"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            try:
                workflow = Workflow.from_yaml(f.name)
                assert workflow.name == "Test Workflow"
                assert len(workflow.agents) == 1
                assert len(workflow.workflow) == 1
            finally:
                os.unlink(f.name)

    def test_yaml_parsing_invalid_file(self):
        with pytest.raises(FileNotFoundError):
            Workflow.from_yaml("nonexistent.yml")

    def test_yaml_parsing_invalid_yaml(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("invalid: yaml: content: [\n")
            f.flush()
            try:
                with pytest.raises(ValueError):
                    Workflow.from_yaml(f.name)
            finally:
                os.unlink(f.name)

    def test_json_serialization(self):
        agent = Agent(model="gpt-4", provider="openai", prompt="Prompt")
        step = AgentStep(type="agent", step="step1", agent="agent1")
        workflow = Workflow(
            name="Test",
            agents={"agent1": agent},
            workflow=[step]
        )
        json_str = workflow.to_json()
        assert '"name": "Test"' in json_str

        # Test deserialization
        workflow2 = Workflow.from_json(json_str)
        assert workflow2.name == workflow.name

class TestTemplateRenderer:
    def test_render_simple(self):
        renderer = TemplateRenderer()
        result = renderer.render("Hello {{name}}", {"name": "World"})
        assert result == "Hello World"

    def test_render_with_fallback(self):
        renderer = TemplateRenderer()
        result = renderer.render_with_fallback("Hello {{name}}", {"name": "World"}, "Default")
        assert result == "Hello World"

        result = renderer.render_with_fallback(None, {}, "Default")
        assert result == "Default"

    def test_render_error(self):
        renderer = TemplateRenderer()
        with pytest.raises(ValueError):
            renderer.render("{{undefined_var}}", {})