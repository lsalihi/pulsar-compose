#!/usr/bin/env python3
"""
Validation script for Pulsar workflow examples.
Tests workflow loading, validation, and basic execution capabilities.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from models.workflow import Workflow

def validate_workflow(file_path: str) -> bool:
    """Validate a single workflow file."""
    try:
        print(f"Validating {file_path}...")
        workflow = Workflow.from_yaml(file_path)

        # Basic validation checks
        assert workflow.version == "0.1", f"Invalid version: {workflow.version}"
        assert workflow.name, "Missing workflow name"
        assert len(workflow.agents) > 0, "No agents defined"
        assert len(workflow.workflow) > 0, "No workflow steps defined"

        # Validate agent references in workflow
        agent_names = set(workflow.agents.keys())
        for step in workflow.workflow:
            if hasattr(step, 'agent'):
                assert step.agent in agent_names, f"Undefined agent: {step.agent}"

        print(f"✅ {workflow.name} - Valid")
        return True

    except Exception as e:
        print(f"❌ {file_path} - Error: {e}")
        return False

def main():
    """Run validation on all example workflows."""
    examples_dir = Path(__file__).parent.parent
    workflow_files = [
        "SIMPLE_CHAIN.yml",
        "CONDITIONAL_REVIEW.yml",
        "TECH_STACK_BUILDER.yml",
        "RESEARCH_ANALYSIS.yml",
        "CUSTOMER_SUPPORT.yml",
        "CODE_REVIEW.yml",
        "DATA_ANALYSIS.yml",
        "CREATIVE_WRITING.yml"
    ]

    print("🔍 Validating Pulsar Workflow Examples")
    print("=" * 50)

    passed = 0
    total = len(workflow_files)

    for filename in workflow_files:
        file_path = examples_dir / filename
        if file_path.exists():
            if validate_workflow(str(file_path)):
                passed += 1
        else:
            print(f"❌ {filename} - File not found")

    print("=" * 50)
    print(f"Results: {passed}/{total} workflows validated successfully")

    # Validate templates
    print("\n🔍 Validating Templates")
    print("-" * 30)

    templates_dir = examples_dir / "templates"
    if templates_dir.exists():
        template_files = list(templates_dir.glob("*.yml"))
        template_passed = 0

        for template_file in template_files:
            if validate_workflow(str(template_file)):
                template_passed += 1

        print(f"Template Results: {template_passed}/{len(template_files)} templates validated")
    else:
        print("❌ Templates directory not found")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)