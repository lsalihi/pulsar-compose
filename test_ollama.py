#!/usr/bin/env python3
"""Test script for Pulsar with Ollama"""

import asyncio
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import modules
from models.workflow import Workflow
from engine.executor import PulsarEngine
from agents.config import PulsarConfig

async def test_ollama():
    print("Testing Pulsar with Ollama...")

    # Load workflow
    workflow = Workflow.from_yaml("examples/simple_chain.yml")
    print(f"Loaded workflow: {workflow.name}")

    # Create agent config (no API keys needed for local)
    config = PulsarConfig()

    # Create executor
    engine = PulsarEngine(workflow, config)

    # Execute
    result = await engine.execute("Create a simple Python function to add two numbers")

    print(f"Execution completed in {result.total_execution_time:.2f}s")
    print(f"Success: {result.success}")

    if result.success:
        print("\nFinal state:")
        for key, value in result.final_state.items():
            print(f"  {key}: {value}")
    else:
        print(f"Error: {result.error}")

    return result

if __name__ == "__main__":
    asyncio.run(test_ollama())