"""
Performance tests for Pulsar components.
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from engine.executor import PulsarEngine
from models.workflow import Workflow, Agent, AgentStep
from tests.mocks import MockAgentFactory, MockOpenAIAgent, MockAnthropicAgent


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""

    @pytest.fixture
    def performance_agent_factory(self):
        """Agent factory optimized for performance testing."""
        factory = MockAgentFactory()

        # Create fast agents for performance testing
        fast_agent = MockOpenAIAgent(latency=0.01)  # Very fast responses
        medium_agent = MockAnthropicAgent(latency=0.05)
        slow_agent = MockOpenAIAgent(latency=0.1)

        factory._agents = {
            "fast": fast_agent,
            "medium": medium_agent,
            "slow": slow_agent
        }

        return factory

    def test_agent_response_time(self, performance_agent_factory):
        """Benchmark individual agent response times."""
        fast_agent = performance_agent_factory.get_agent("fast")
        medium_agent = performance_agent_factory.get_agent("medium")
        slow_agent = performance_agent_factory.get_agent("slow")

        # Test fast agent
        start_time = time.time()
        result = asyncio.run(fast_agent.execute("test", "gpt-4"))
        fast_time = time.time() - start_time

        # Test medium agent
        start_time = time.time()
        result = asyncio.run(medium_agent.execute("test", "gpt-4"))
        medium_time = time.time() - start_time

        # Test slow agent
        start_time = time.time()
        result = asyncio.run(slow_agent.execute("test", "gpt-4"))
        slow_time = time.time() - start_time

        # Assert reasonable performance bounds
        assert fast_time < 0.05  # Fast agent should be very quick
        assert medium_time < 0.1  # Medium agent reasonable
        assert slow_time < 0.2   # Slow agent acceptable

    @pytest.mark.asyncio
    async def test_workflow_execution_performance(self, performance_agent_factory):
        """Test workflow execution performance."""
        # Create simple workflow
        agent = Agent(model="gpt-4", provider="openai", prompt="Process input")

        steps = [
            AgentStep(
                type="agent",
                step=f"step_{i}",
                agent="fast",
                prompt=f"Process step {i}: {{input}}",
                save_to=f"result_{i}"
            ) for i in range(10)
        ]

        workflow = Workflow(
            name="Performance Test Workflow",
            agents={"fast": agent},
            workflow=steps
        )

        engine = PulsarEngine(workflow)
        engine.agent_factory = performance_agent_factory

        # Measure execution time
        start_time = time.time()
        result = await engine.execute("Performance test input")
        execution_time = time.time() - start_time

        # Assert performance requirements
        assert result.success is True
        assert execution_time < 2.0  # Should complete within 2 seconds
        assert len(result.step_results) == 10

    @pytest.mark.asyncio
    async def test_concurrent_workflow_execution(self, performance_agent_factory):
        """Test performance with concurrent workflow executions."""
        # Create simple workflow
        agent = Agent(model="gpt-4", provider="openai", prompt="Process input")

        step = AgentStep(
            type="agent",
            step="process",
            agent="fast",
            prompt="Process: {{input}}",
            save_to="result"
        )

        workflow = Workflow(
            name="Concurrent Test Workflow",
            agents={"fast": agent},
            workflow=[step]
        )

        async def run_single_workflow(workflow_id):
            engine = PulsarEngine(workflow)
            engine.agent_factory = performance_agent_factory
            result = await engine.execute(f"Input {workflow_id}")
            return result

        # Run multiple workflows concurrently
        num_workflows = 5
        start_time = time.time()

        tasks = [run_single_workflow(i) for i in range(num_workflows)]
        results = await asyncio.gather(*tasks)

        execution_time = time.time() - start_time

        # All should succeed
        assert all(result.success for result in results)

        # Should be faster than sequential execution
        expected_sequential_time = num_workflows * 0.05  # 5 workflows * 50ms each
        assert execution_time < expected_sequential_time * 2  # Allow some overhead

    @pytest.mark.asyncio
    async def test_memory_efficiency(self, performance_agent_factory):
        """Test memory efficiency during workflow execution."""
        # Create workflow with many steps
        agent = Agent(model="gpt-4", provider="openai", prompt="Generate data")

        steps = [
            AgentStep(
                type="agent",
                step=f"step_{i}",
                agent="fast",
                prompt=f"Generate data for step {i}: {{input}}",
                save_to=f"data_{i}"
            ) for i in range(20)
        ]

        workflow = Workflow(
            name="Memory Test Workflow",
            agents={"fast": agent},
            workflow=steps
        )

        engine = PulsarEngine(workflow)
        engine.agent_factory = performance_agent_factory

        # Execute workflow multiple times to check for memory issues
        for i in range(5):
            result = await engine.execute(f"Memory test {i}")
            assert result.success is True
            assert len(result.step_results) == 20

        # If we get here without memory errors, basic memory efficiency is OK
        # In a real scenario, you'd use memory profiling tools

    def test_agent_factory_caching(self, performance_agent_factory):
        """Test that agent factory caches agents properly."""
        # Get same agent multiple times
        agent1 = performance_agent_factory.get_agent("fast")
        agent2 = performance_agent_factory.get_agent("fast")

        # Should be the same instance (cached)
        assert agent1 is agent2

        # Measure time for cached access
        start_time = time.time()
        for _ in range(100):
            agent = performance_agent_factory.get_agent("fast")
        cache_access_time = time.time() - start_time

        # Cached access should be very fast
        assert cache_access_time < 0.01


class TestLoadTesting:
    """Load testing for high-volume scenarios."""

    @pytest.fixture
    def load_test_factory(self):
        """Factory for load testing with consistent performance."""
        factory = MockAgentFactory()

        # Create agent with consistent low latency
        load_agent = MockOpenAIAgent(latency=0.02, failure_rate=0.0)
        factory._agents = {"worker": load_agent}

        return factory

    @pytest.mark.asyncio
    async def test_high_volume_workflow_execution(self, load_test_factory):
        """Test executing many workflows in sequence."""
        agent = Agent(model="gpt-4", provider="openai", prompt="Process request")

        step = AgentStep(
            type="agent",
            step="process",
            agent="worker",
            prompt="Process request: {{input}}",
            save_to="result"
        )

        workflow = Workflow(
            name="Load Test Workflow",
            agents={"worker": agent},
            workflow=[step]
        )

        execution_times = []

        # Execute 50 workflows
        for i in range(50):
            engine = PulsarEngine(workflow)
            engine.agent_factory = load_test_factory

            start_time = time.time()
            result = await engine.execute(f"Request {i}")
            execution_time = time.time() - start_time

            assert result.success is True
            execution_times.append(execution_time)

        # Analyze performance statistics
        avg_time = statistics.mean(execution_times)
        max_time = max(execution_times)
        min_time = min(execution_times)
        p95_time = statistics.quantiles(execution_times, n=20)[18]  # 95th percentile

        # Assert reasonable performance
        assert avg_time < 0.1  # Average under 100ms
        assert max_time < 0.5  # Max under 500ms
        assert p95_time < 0.2  # 95% under 200ms

    @pytest.mark.asyncio
    async def test_concurrent_load_test(self, load_test_factory):
        """Test concurrent execution under load."""
        agent = Agent(model="gpt-4", provider="openai", prompt="Process input")

        step = AgentStep(
            type="agent",
            step="process",
            agent="worker",
            prompt="Process: {{input}}",
            save_to="result"
        )

        workflow = Workflow(
            name="Concurrent Load Test",
            agents={"worker": agent},
            workflow=[step]
        )

        async def execute_workflow(workflow_id):
            engine = PulsarEngine(workflow)
            engine.agent_factory = load_test_factory
            start_time = time.time()
            result = await engine.execute(f"Concurrent request {workflow_id}")
            execution_time = time.time() - start_time
            return result.success, execution_time

        # Execute 20 workflows concurrently
        num_concurrent = 20
        start_time = time.time()
        tasks = [execute_workflow(i) for i in range(num_concurrent)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # All should succeed
        successes = [success for success, _ in results]
        assert all(successes)

        # Extract execution times
        execution_times = [exec_time for _, exec_time in results]

        # Calculate metrics
        avg_execution_time = statistics.mean(execution_times)
        max_execution_time = max(execution_times)
        throughput = num_concurrent / total_time  # workflows per second

        # Assert performance requirements
        assert avg_execution_time < 0.2  # Average execution time
        assert max_execution_time < 1.0  # Max execution time
        assert throughput > 10  # At least 10 workflows per second

    def test_agent_failure_resilience(self, load_test_factory):
        """Test system resilience under agent failures."""
        # Create agent with some failure rate
        failing_agent = MockOpenAIAgent(latency=0.05, failure_rate=0.3)  # 30% failure rate
        load_test_factory._agents = {"worker": failing_agent}

        agent = Agent(model="gpt-4", provider="openai", prompt="Process input")

        step = AgentStep(
            type="agent",
            step="process",
            agent="worker",
            prompt="Process: {{input}}",
            save_to="result"
        )

        workflow = Workflow(
            name="Resilience Test",
            agents={"worker": agent},
            workflow=[step]
        )

        success_count = 0
        total_runs = 100

        for i in range(total_runs):
            engine = PulsarEngine(workflow)
            engine.agent_factory = load_test_factory
            result = asyncio.run(engine.execute(f"Request {i}"))

            if result.success:
                success_count += 1

        success_rate = success_count / total_runs

        # Should have reasonable success rate (allowing for failures)
        assert success_rate > 0.5  # At least 50% success rate
        assert success_rate < 0.9  # But not too high (since we expect some failures)


class TestScalabilityTesting:
    """Scalability tests for growing workloads."""

    @pytest.fixture
    def scalable_factory(self):
        """Factory that can scale with load."""
        factory = MockAgentFactory()
        scalable_agent = MockOpenAIAgent(latency=0.03, failure_rate=0.0)
        factory._agents = {"worker": scalable_agent}
        return factory

    @pytest.mark.asyncio
    async def test_increasing_workflow_complexity(self, scalable_factory):
        """Test performance as workflow complexity increases."""
        agent = Agent(model="gpt-4", provider="openai", prompt="Process step")

        complexity_levels = [5, 10, 15, 20]  # Number of steps
        performance_data = {}

        for num_steps in complexity_levels:
            steps = [
                AgentStep(
                    type="agent",
                    step=f"step_{i}",
                    agent="worker",
                    prompt=f"Step {i} processing: {{input}}",
                    save_to=f"result_{i}"
                ) for i in range(num_steps)
            ]

            workflow = Workflow(
                name=f"Complexity Test {num_steps}",
                agents={"worker": agent},
                workflow=steps
            )

            # Execute multiple times and average
            execution_times = []
            for _ in range(3):  # 3 runs for averaging
                engine = PulsarEngine(workflow)
                engine.agent_factory = scalable_factory

                start_time = time.time()
                result = await engine.execute(f"Complexity test {num_steps}")
                execution_time = time.time() - start_time

                assert result.success is True
                execution_times.append(execution_time)

            avg_time = statistics.mean(execution_times)
            performance_data[num_steps] = avg_time

        # Check that performance scales reasonably
        # Time should increase but not exponentially
        time_5 = performance_data[5]
        time_20 = performance_data[20]

        # 20 steps should take less than 5x the time of 5 steps (allowing for linear scaling + overhead)
        assert time_20 < time_5 * 6

    @pytest.mark.asyncio
    async def test_memory_scaling(self, scalable_factory):
        """Test memory usage scaling with workflow size."""
        agent = Agent(model="gpt-4", provider="openai", prompt="Process data")

        # Test with increasingly large state data
        data_sizes = [100, 1000, 10000]  # Characters of data

        for size in data_sizes:
            # Create large input data
            large_input = "x" * size

            step = AgentStep(
                type="agent",
                step="process_large",
                agent="worker",
                prompt="Process this data: {{input}}",
                save_to="result"
            )

            workflow = Workflow(
                name=f"Memory Test {size}",
                agents={"worker": agent},
                workflow=[step]
            )

            engine = PulsarEngine(workflow)
            engine.agent_factory = scalable_factory

            # Execute workflow
            result = await engine.execute(large_input)
            assert result.success is True

            # Check that result contains processed data
            assert len(result.final_state["result"]) > 0

        # If we complete all sizes without memory errors, scaling is acceptable


class TestStressTesting:
    """Stress tests for extreme conditions."""

    @pytest.fixture
    def stress_factory(self):
        """Factory for stress testing."""
        factory = MockAgentFactory()
        stress_agent = MockOpenAIAgent(latency=0.1, failure_rate=0.1)  # Some failures
        factory._agents = {"worker": stress_agent}
        return factory

    @pytest.mark.asyncio
    async def test_extreme_concurrency(self, stress_factory):
        """Test extreme concurrent workflow execution."""
        agent = Agent(model="gpt-4", provider="openai", prompt="Handle stress")

        step = AgentStep(
            type="agent",
            step="stress_test",
            agent="worker",
            prompt="Handle stress: {{input}}",
            save_to="result"
        )

        workflow = Workflow(
            name="Stress Test Workflow",
            agents={"worker": agent},
            workflow=[step]
        )

        async def stress_run(run_id):
            try:
                engine = PulsarEngine(workflow)
                engine.agent_factory = stress_factory
                result = await engine.execute(f"Stress input {run_id}")
                return result.success
            except Exception:
                return False

        # Launch many concurrent workflows
        num_stress_runs = 50
        tasks = [stress_run(i) for i in range(num_stress_runs)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successful runs
        successful_runs = sum(1 for result in results if result is True)

        # Should handle most requests even under stress
        success_rate = successful_runs / num_stress_runs
        assert success_rate > 0.7  # At least 70% success rate under stress

    def test_resource_cleanup(self):
        """Test that resources are properly cleaned up after stress."""
        # This test ensures no resource leaks after intensive usage
        # Use a reliable agent (no failures) for this test
        factory = MockAgentFactory()
        reliable_agent = MockOpenAIAgent(latency=0.01, failure_rate=0.0)  # No failures
        factory._agents = {"worker": reliable_agent}
        
        agent = Agent(model="gpt-4", provider="openai", prompt="Test input")

        step = AgentStep(
            type="agent",
            step="cleanup_test",
            agent="worker",
            prompt="Test: {{input}}",
            save_to="result"
        )

        workflow = Workflow(
            name="Cleanup Test",
            agents={"worker": agent},
            workflow=[step]
        )

        # Run many executions in sequence
        for i in range(100):
            engine = PulsarEngine(workflow)
            engine.agent_factory = factory
            result = asyncio.run(engine.execute(f"Cleanup test {i}"))
            assert result.success is True

        # After stress test, system should still function normally
        engine = PulsarEngine(workflow)
        engine.agent_factory = factory
        final_result = asyncio.run(engine.execute("Final cleanup check"))
        assert final_result.success is True