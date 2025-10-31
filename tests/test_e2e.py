"""
End-to-end tests for Pulsar workflows.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, AsyncMock

from engine.executor import PulsarEngine
from models.workflow import Workflow
from tests.mocks import MockAgentFactory, MockOpenAIAgent, MockAnthropicAgent, MockLocalAgent


class TestEndToEndWorkflows:
    """End-to-end workflow tests."""

    @pytest.fixture
    def e2e_agent_factory(self):
        """Agent factory for E2E tests with realistic responses."""
        factory = MockAgentFactory()

        # Create agents with realistic response patterns
        content_writer = MockOpenAIAgent(
            response_template="""# {prompt}

## Introduction
This is a comprehensive guide about the requested topic.

## Key Points
- Point 1: Important information
- Point 2: More details
- Point 3: Additional insights

## Conclusion
Summary of the main points discussed.""",
            latency=0.2
        )

        code_reviewer = MockAnthropicAgent(
            response_template="""Code Review for: {prompt}

## Issues Found
- Style: Good code formatting
- Logic: Logic appears sound
- Performance: No obvious performance issues

## Recommendations
- Consider adding error handling
- Add unit tests for edge cases

## Overall Assessment
Code quality: Good (8/10)""",
            latency=0.3
        )

        data_analyzer = MockLocalAgent(
            response_template="""Data Analysis Results for: {prompt}

## Summary Statistics
- Total records: 1000
- Average value: 45.67
- Standard deviation: 12.34

## Key Findings
- Trend: Increasing over time
- Outliers: 2% of data points
- Correlations: Strong positive correlation with variable X

## Recommendations
- Further investigation needed for outliers
- Consider predictive modeling""",
            latency=0.1
        )

        factory._agents = {
            "openai": content_writer,
            "anthropic": code_reviewer,
            "local": data_analyzer
        }

        return factory

    @pytest.mark.asyncio
    async def test_content_creation_workflow(self, e2e_agent_factory):
        """Test complete content creation workflow."""
        from models.workflow import Agent, AgentStep

        # Define agents (using the same names as in the fixture)
        writer = Agent(model="gpt-4", provider="openai", prompt="Default writing prompt")
        reviewer = Agent(model="claude-3", provider="anthropic", prompt="Default review prompt")

        # Define workflow steps
        research_step = AgentStep(
            type="agent",
            step="research_topic",
            agent="writer",
            prompt="Research and outline key points for: {{input}}",
            save_to="research"
        )

        write_step = AgentStep(
            type="agent",
            step="write_content",
            agent="writer",
            prompt="Write a comprehensive article using this research: {{research}}",
            save_to="article"
        )

        review_step = AgentStep(
            type="agent",
            step="review_content",
            agent="reviewer",
            prompt="Review and provide feedback on this article: {{article}}",
            save_to="review"
        )

        workflow = Workflow(
            name="Content Creation E2E",
            agents={"writer": writer, "reviewer": reviewer},
            workflow=[research_step, write_step, review_step]
        )

        # Execute workflow
        engine = PulsarEngine(workflow)
        engine.agent_factory = e2e_agent_factory

        result = await engine.execute("Machine Learning Best Practices")

        # Verify complete execution
        assert result.success is True
        assert len(result.step_results) == 3

        # Check each step completed successfully
        for step_result in result.step_results:
            assert step_result.success is True

        # Verify content flow
        research = result.final_state["research"]
        article = result.final_state["article"]
        review = result.final_state["review"]

        # The mock agents return templates with the prompt, so check for expected content
        assert "Machine Learning Best Practices" in research
        assert "comprehensive guide" in article  # This should be in the writer template
        assert "Code Review for:" in review  # This should be in the reviewer template

    @pytest.mark.asyncio
    async def test_code_review_workflow(self, e2e_agent_factory):
        """Test code review workflow end-to-end."""
        from models.workflow import Agent, AgentStep

        reviewer = Agent(model="claude-3", provider="anthropic", prompt="Review code")

        analyze_step = AgentStep(
            type="agent",
            step="analyze_code",
            agent="reviewer",
            prompt="Analyze this code for quality and issues: {{input}}",
            save_to="analysis"
        )

        review_step = AgentStep(
            type="agent",
            step="provide_feedback",
            agent="reviewer",
            prompt="Provide detailed review feedback for: {{analysis}}",
            save_to="feedback"
        )

        workflow = Workflow(
            name="Code Review E2E",
            agents={"reviewer": reviewer},
            workflow=[analyze_step, review_step]
        )

        engine = PulsarEngine(workflow)
        engine.agent_factory = e2e_agent_factory

        code_sample = """
def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
"""

        result = await engine.execute(code_sample)

        assert result.success is True
        assert len(result.step_results) == 2

        analysis = result.final_state["analysis"]
        feedback = result.final_state["feedback"]

        assert "Issues Found" in analysis
        assert "Recommendations" in feedback

    @pytest.mark.asyncio
    async def test_data_analysis_workflow(self, e2e_agent_factory):
        """Test data analysis workflow."""
        from models.workflow import Agent, AgentStep

        analyzer = Agent(model="local-llm", provider="local", prompt="Analyze data")

        process_step = AgentStep(
            type="agent",
            step="process_data",
            agent="analyzer",
            prompt="Process and analyze this dataset: {{input}}",
            save_to="processed_data"
        )

        analyze_step = AgentStep(
            type="agent",
            step="analyze_results",
            agent="analyzer",
            prompt="Provide insights from this processed data: {{processed_data}}",
            save_to="insights"
        )

        workflow = Workflow(
            name="Data Analysis E2E",
            agents={"analyzer": analyzer},
            workflow=[process_step, analyze_step]
        )

        engine = PulsarEngine(workflow)
        engine.agent_factory = e2e_agent_factory

        # Mock dataset description
        dataset = "Sales data: 1000 records, columns: date, product, revenue, region"

        result = await engine.execute(dataset)

        assert result.success is True
        assert len(result.step_results) == 2

        processed = result.final_state["processed_data"]
        insights = result.final_state["insights"]

        assert "Summary Statistics" in processed
        assert "Key Findings" in insights

    @pytest.mark.asyncio
    async def test_conditional_workflow_e2e(self):
        """Test conditional workflow execution."""
        from models.workflow import Agent, AgentStep, ConditionalStep

        writer = Agent(model="gpt-4", provider="openai", prompt="Write content")
        reviewer = Agent(model="claude-3", provider="anthropic", prompt="Review content")

        # Initial content creation
        write_step = AgentStep(
            type="agent",
            step="write_draft",
            agent="writer",
            prompt="Write a draft about: {{input}}",
            save_to="draft"
        )

        # Review step
        review_step = AgentStep(
            type="agent",
            step="review_content",
            agent="reviewer",
            prompt="Review this content: {{draft}}",
            save_to="review"
        )

        # Expansion step
        expand_step = AgentStep(
            type="agent",
            step="expand_content",
            agent="writer",
            prompt="Expand this draft to be more comprehensive: {{draft}}",
            save_to="expanded_draft"
        )

        # Quality check condition
        quality_condition = ConditionalStep(
            type="conditional",
            step="check_quality",
            **{"if": "length(draft) > 500"},
            then=[review_step],
            else_=[expand_step]
        )

        workflow = Workflow(
            name="Conditional Workflow E2E",
            agents={"writer": writer, "reviewer": reviewer},
            workflow=[write_step, quality_condition]
        )

        # Test with short content (should expand)
        factory = MockAgentFactory()
        short_writer = MockOpenAIAgent(
            response_template="Short draft: {prompt}",  # Less than 500 chars
            latency=0.001
        )
        reviewer_agent = MockAnthropicAgent(
            response_template="Review: {prompt}",
            latency=0.001
        )

        factory._agents = {
            "writer": short_writer,
            "reviewer": reviewer_agent
        }

        engine = PulsarEngine(workflow)
        engine.agent_factory = factory

        result = await engine.execute("Test topic")

        assert result.success is True
        # Should have executed: write_draft, check_quality (with branch)
        assert len(result.step_results) == 2

        # Check step results
        write_step = result.step_results[0]
        condition_step = result.step_results[1]

        assert write_step.step_name == "write_draft"
        assert condition_step.step_name == "check_quality"
        assert write_step.success is True
        assert condition_step.success is True

        # Check that condition evaluated to false and took else branch
        assert condition_step.output["condition_result"] is False
        assert condition_step.output["branch"] == "else"
        
        # Check that expand_content was executed in the branch
        branch_results = condition_step.metadata["branch_results"]
        assert len(branch_results) == 1
        assert branch_results[0]["step_name"] == "expand_content"
        assert branch_results[0]["success"] is True

        # Check that expand_content step was NOT executed at top level
        step_names = [step.step_name for step in result.step_results]
        assert "expand_content" not in step_names
        assert "review_content" not in step_names

    @pytest.mark.asyncio
    async def test_workflow_with_file_input(self):
        """Test workflow that reads from file input."""
        from models.workflow import Agent, AgentStep

        analyzer = Agent(model="local-llm", provider="local", prompt="Analyze files")

        analyze_file_step = AgentStep(
            type="agent",
            step="analyze_file",
            agent="analyzer",
            prompt="Analyze the contents of this file: {{file_content}}",
            save_to="analysis"
        )

        workflow = Workflow(
            name="File Analysis E2E",
            agents={"analyzer": analyzer},
            workflow=[analyze_file_step]
        )

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Sample file content for analysis.\nThis contains multiple lines.\nEnd of file.")
            temp_file = f.name

        try:
            # Mock file reading
            factory = MockAgentFactory()
            analyzer_agent = MockLocalAgent(
                response_template="File analysis: {prompt}",
                latency=0.001
            )
            factory._agents = {"analyzer": analyzer_agent}

            engine = PulsarEngine(workflow)
            engine.agent_factory = factory

            # Simulate file content in state
            file_content = "Sample file content for analysis.\nThis contains multiple lines.\nEnd of file."
            result = await engine.execute_with_initial_state({"file_content": file_content})

            assert result.success is True
            assert len(result.step_results) == 1
            assert "File analysis:" in result.step_results[0].output

        finally:
            # Clean up
            os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_multi_agent_collaboration(self):
        """Test multi-agent collaboration workflow."""
        from models.workflow import Agent, AgentStep

        researcher = Agent(model="gpt-4", provider="openai", prompt="Research topics")
        writer = Agent(model="claude-3", provider="anthropic", prompt="Write articles")
        editor = Agent(model="gpt-4", provider="openai", prompt="Edit content")

        # Research phase
        research_step = AgentStep(
            type="agent",
            step="research",
            agent="researcher",
            prompt="Research comprehensive information about: {{input}}",
            save_to="research_data"
        )

        # Writing phase
        write_step = AgentStep(
            type="agent",
            step="write_draft",
            agent="writer",
            prompt="Write a detailed article using this research: {{research_data}}",
            save_to="draft"
        )

        # Editing phase
        edit_step = AgentStep(
            type="agent",
            step="edit_final",
            agent="editor",
            prompt="Edit and polish this article: {{draft}}",
            save_to="final_article"
        )

        workflow = Workflow(
            name="Multi-Agent Collaboration E2E",
            agents={
                "researcher": researcher,
                "writer": writer,
                "editor": editor
            },
            workflow=[research_step, write_step, edit_step]
        )

        # Create agents with different response styles
        factory = MockAgentFactory()
        research_agent = MockOpenAIAgent(
            response_template="Research findings: {prompt} - Key data points discovered",
            latency=0.001
        )
        writing_agent = MockAnthropicAgent(
            response_template="Written article: {prompt} - Comprehensive coverage provided",
            latency=0.001
        )
        editing_agent = MockOpenAIAgent(
            response_template="Edited version: {prompt} - Polished and refined",
            latency=0.001
        )

        factory._agents = {
            "researcher": research_agent,
            "writer": writing_agent,
            "editor": editing_agent
        }

        engine = PulsarEngine(workflow)
        engine.agent_factory = factory

        result = await engine.execute("Artificial Intelligence Ethics")

        assert result.success is True
        assert len(result.step_results) == 3

        # Verify each agent contributed
        research_output = result.step_results[0].output
        write_output = result.step_results[1].output
        edit_output = result.step_results[2].output

        assert "Research findings:" in research_output
        assert "Written article:" in write_output
        assert "Edited version:" in edit_output

        # Verify content flow through the pipeline
        assert "Artificial Intelligence Ethics" in research_output


class TestWorkflowPerformance:
    """Performance tests for workflows."""

    @pytest.mark.asyncio
    async def test_workflow_execution_time(self):
        """Test that workflows complete within reasonable time."""
        from models.workflow import Agent, AgentStep

        agent = Agent(model="gpt-4", provider="openai", prompt="Process steps")

        steps = []
        for i in range(5):
            step = AgentStep(
                type="agent",
                step=f"step_{i}",
                agent="worker",
                prompt=f"Process step {i}: {{input}}",
                save_to=f"result_{i}"
            )
            steps.append(step)

        workflow = Workflow(
            name="Performance Test Workflow",
            agents={"worker": agent},
            workflow=steps
        )

        factory = MockAgentFactory()
        fast_agent = MockOpenAIAgent(latency=0.001)  # Fast responses
        factory._agents = {"worker": fast_agent}

        engine = PulsarEngine(workflow)
        engine.agent_factory = factory

        start_time = asyncio.get_event_loop().time()
        result = await engine.execute("Performance test input")
        end_time = asyncio.get_event_loop().time()

        execution_time = end_time - start_time

        # Should complete in reasonable time (allowing for some overhead)
        assert execution_time < 1.0  # Less than 1 second for 5 fast steps
        assert result.success is True
        assert len(result.step_results) == 5

    @pytest.mark.asyncio
    async def test_memory_usage_stability(self):
        """Test that workflow execution doesn't have memory leaks."""
        # This is a basic test - in a real scenario you'd use memory profiling
        from models.workflow import Agent, AgentStep

        agent = Agent(model="gpt-4", provider="openai", prompt="Process data")

        step = AgentStep(
            type="agent",
            step="memory_test",
            agent="worker",
            prompt="Process: {{input}}",
            save_to="result"
        )

        workflow = Workflow(
            name="Memory Test Workflow",
            agents={"worker": agent},
            workflow=[step]
        )

        factory = MockAgentFactory()
        factory._agents = {"worker": MockOpenAIAgent()}

        engine = PulsarEngine(workflow)
        engine.agent_factory = factory

        # Run multiple executions
        for i in range(10):
            result = await engine.execute(f"Test input {i}")
            assert result.success is True

        # Basic check that execution still works after multiple runs
        final_result = await engine.execute("Final test")
        assert final_result.success is True


class TestWorkflowErrorRecovery:
    """Error recovery tests for workflows."""

    @pytest.mark.asyncio
    async def test_partial_failure_recovery(self):
        """Test workflow behavior when some steps fail."""
        from models.workflow import Agent, AgentStep

        agent = Agent(model="gpt-4", provider="openai", prompt="Process data")

        # Create workflow with mix of reliable and unreliable steps
        reliable_step = AgentStep(
            type="agent",
            step="reliable_step",
            agent="worker",
            prompt="Reliable processing: {{input}}",
            save_to="reliable_result"
        )

        unreliable_step = AgentStep(
            type="agent",
            step="unreliable_step",
            agent="worker",
            prompt="Unreliable processing: {{input}}",
            save_to="unreliable_result"
        )

        workflow = Workflow(
            name="Error Recovery Test",
            agents={"worker": agent},
            workflow=[reliable_step, unreliable_step]
        )

        # Create factory with mixed success rates
        factory = MockAgentFactory()
        reliable_agent = MockOpenAIAgent(failure_rate=0.0)  # Never fails
        unreliable_agent = MockOpenAIAgent(failure_rate=1.0)  # Always fails

        factory._agents = {
            "worker": reliable_agent  # Use reliable for first step
        }

        engine = PulsarEngine(workflow)
        engine.agent_factory = factory

        # First execution with reliable agent
        result1 = await engine.execute("Test input")
        assert result1.success is True
        assert result1.step_results[0].success is True

        # Switch to unreliable agent and test error handling
        factory._agents = {"worker": unreliable_agent}
        result2 = await engine.execute("Test input 2")
        assert result2.success is False
        assert result2.step_results[0].success is False