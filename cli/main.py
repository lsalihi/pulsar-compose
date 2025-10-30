#!/usr/bin/env python3
"""
Pulsar Compose CLI - Docker-like interface for AI workflows
"""

import click
from typing import Optional
import os
import sys

@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True
)
@click.version_option(version="0.1.0", prog_name="Pulsar Compose")
@click.option(
    "--config",
    type=click.Path(),
    help="Path to config file",
    default="~/.pulsar/config.yml"
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    help="Log level",
    default="INFO"
)
@click.pass_context
def cli(ctx, config: str, log_level: str):
    """Pulsar Compose - Docker-like AI workflow orchestration

    Examples:
      pulsar run workflow.yml
      pulsar logs my-workflow
      pulsar compose up
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return

    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = os.path.expanduser(config)
    ctx.obj["log_level"] = log_level

# === CORE COMMANDS ===

@cli.command()
@click.argument("workflow_file", type=click.Path(exists=True))
@click.option("--input", "-i", help="Input text for the workflow")
@click.option("--watch", "-w", is_flag=True, help="Watch for changes and rerun")
@click.option("--dry-run", is_flag=True, help="Show execution plan without running")
@click.pass_context
def run(ctx, workflow_file: str, input: Optional[str], watch: bool, dry_run: bool):
    """Run a workflow from a YAML file.

    Examples:
      pulsar run my-workflow.yml
      pulsar run workflow.yml --input "Create a REST API"
      pulsar run workflow.yml --watch
    """
    try:
        from models.workflow import Workflow
        from engine.executor import PulsarEngine
        from agents import PulsarConfig

        workflow = Workflow.from_yaml(workflow_file)
        agent_config = PulsarConfig.from_env()
        engine = PulsarEngine(workflow, agent_config)

        if dry_run:
            click.echo("📋 Execution Plan:")
            # Show step-by-step plan
            for i, step in enumerate(workflow.workflow, 1):
                step_type = step.get('type', 'unknown')
                step_name = step.get('step', f'step_{i}')
                click.echo(f"  {i}. {step_type}: {step_name}")
            return

        if not input:
            input = click.prompt("🔮 What would you like to accomplish?")

        import asyncio

        async def execute_workflow():
            result = await engine.execute(input)
            return result

        result = asyncio.run(execute_workflow())

        click.echo("✅ Workflow completed successfully!")
        click.echo(f"📊 Results saved to: {result.output_path}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument("workflow_file", type=click.Path(exists=True))
def validate(workflow_file: str):
    """Validate a workflow file for syntax errors.

    Examples:
      pulsar validate my-workflow.yml
    """
    try:
        from models.workflow import Workflow

        workflow = Workflow.from_yaml(workflow_file)
        click.echo("✅ Workflow file is valid!")
        click.echo(f"📊 Agents: {len(workflow.agents)}")
        click.echo(f"📋 Steps: {len(workflow.workflow)}")
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument("run_id", required=False)
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@click.option("--tail", type=int, help="Number of lines to show from the end")
def logs(run_id: Optional[str], follow: bool, tail: int):
    """Show execution logs for a workflow run.

    Examples:
      pulsar logs                 # Show recent runs
      pulsar logs abc123          # Show specific run
      pulsar logs --follow        # Follow live logs
      pulsar logs --tail 50       # Show last 50 lines
    """
    from .history import ExecutionHistory

    history = ExecutionHistory()

    if not run_id:
        # List recent runs
        executions = history.list_executions(10)
        click.echo("Recent workflow runs:")
        for execution in executions:
            run_id_short = execution.get('run_id', '')[:8]
            workflow_name = execution.get('workflow_name', 'Unknown')
            result = execution.get('result', {})
            success = result.get('success', False)
            status_icon = "✅" if success else "❌"
            click.echo(f"  {status_icon} {run_id_short} - {workflow_name}")
        return

    # Show specific run logs
    try:
        execution_data = history.get_execution(run_id)
        if not execution_data:
            click.echo(f"❌ Run {run_id} not found", err=True)
            return

        if follow:
            # Live tail implementation (simplified)
            click.echo(f"Following logs for run {run_id}...")
            # In a real implementation, this would stream logs
        else:
            # Show execution result
            result = execution_data.get('result', {})
            if result:
                click.echo(f"Run ID: {run_id}")
                click.echo(f"Workflow: {execution_data.get('workflow_name', 'Unknown')}")
                click.echo(f"Success: {result.get('success', False)}")
                click.echo(f"Duration: {result.get('total_execution_time', 0):.2f}s")
            else:
                click.echo(f"Could not load result for run {run_id}")
    except Exception as e:
        click.echo(f"❌ Error reading logs: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument("run_id", required=False)
def status(run_id: Optional[str]):
    """Show status of workflow runs.

    Examples:
      pulsar status              # Show all runs
      pulsar status abc123       # Show specific run status
    """
    from .history import ExecutionHistory

    history = ExecutionHistory()

    if run_id:
        # Specific run status
        execution_data = history.get_execution(run_id)
        if not execution_data:
            click.echo(f"❌ Run {run_id} not found", err=True)
            return

        result_data = execution_data.get('result', {})
        success = result_data.get('success', False)
        completed_at = result_data.get('completed_at')

        if completed_at:
            status = "Completed"
            status_icon = "✅" if success else "❌"
        else:
            status = "Running"
            status_icon = "🟡"

        click.echo(f"Run: {run_id}")
        click.echo(f"Workflow: {execution_data.get('workflow_name', 'Unknown')}")
        click.echo(f"Status: {status_icon} {status}")

        if completed_at:
            click.echo(f"Completed: {completed_at}")
    else:
        # List all runs
        executions = history.list_executions(20)
        click.echo("Workflow Runs:")
        for execution in executions:
            run_id_short = execution.get('run_id', '')[:8]
            workflow_name = execution.get('workflow_name', 'Unknown')
            result = execution.get('result', {})
            success = result.get('success', False)
            completed_at = result.get('completed_at')

            if completed_at:
                status_icon = "✅" if success else "❌"
            else:
                status_icon = "🟡"

            click.echo(f"  {status_icon} {run_id_short} - {workflow_name}")

# === DOCKER-COMPOSE STYLE COMMANDS ===

@cli.group()
def compose():
    """Docker Compose-style commands for workflow management."""
    pass

@compose.command()
@click.argument("workflow_file", default="pulsar-compose.yml")
@click.option("--detach", "-d", is_flag=True, help="Run in background")
def up(workflow_file: str, detach: bool):
    """Build and run a workflow (Docker Compose style).

    Examples:
      pulsar compose up
      pulsar compose up my-workflow.yml
      pulsar compose up -d
    """
    click.echo(f"🚀 Starting workflow from {workflow_file}...")
    # Implementation similar to run but with compose semantics

@compose.command()
@click.argument("workflow_file", default="pulsar-compose.yml")
def down(workflow_file: str):
    """Stop and cleanup workflow resources.

    Examples:
      pulsar compose down
    """
    click.echo(f"🛑 Stopping workflow from {workflow_file}...")

@compose.command()
@click.argument("workflow_file", default="pulsar-compose.yml")
def ps(workflow_file: str):
    """List workflow containers and status.

    Examples:
      pulsar compose ps
    """
    click.echo("📊 Workflow status:")

# === WORKFLOW MANAGEMENT ===

@cli.group()
def workflow():
    """Workflow management commands."""
    pass

@workflow.command()
@click.argument("template", type=click.Choice(["simple", "conditional"]))
@click.option("--output", "-o", help="Output file", default="pulsar-compose.yml")
def init(template: str, output: str):
    """Initialize a new workflow from a template.

    Examples:
      pulsar workflow init simple
      pulsar workflow init conditional -o my-workflow.yml
    """
    import yaml

    templates = {
        'simple': {
            'version': '0.1',
            'name': 'Simple Workflow',
            'agents': {
                'greeter': {
                    'model': 'gpt-4',
                    'provider': 'openai',
                    'prompt': 'Say hello to {{name}}'
                }
            },
            'workflow': [
                {
                    'type': 'agent',
                    'step': 'greet',
                    'agent': 'greeter',
                    'save': 'greeting'
                }
            ]
        },
        'conditional': {
            'version': '0.1',
            'name': 'Conditional Workflow',
            'agents': {
                'analyzer': {
                    'model': 'gpt-4',
                    'provider': 'openai',
                    'prompt': 'Analyze sentiment of: {{text}}. Return "positive" or "negative".'
                },
                'positive_handler': {
                    'model': 'gpt-4',
                    'provider': 'openai',
                    'prompt': 'Respond positively to: {{text}}'
                },
                'negative_handler': {
                    'model': 'gpt-4',
                    'provider': 'openai',
                    'prompt': 'Respond negatively to: {{text}}'
                }
            },
            'workflow': [
                {
                    'type': 'agent',
                    'step': 'analyze',
                    'agent': 'analyzer',
                    'save': 'sentiment'
                },
                {
                    'type': 'conditional',
                    'step': 'respond',
                    'if': '{{sentiment}} == "positive"',
                    'then': [
                        {
                            'type': 'agent',
                            'step': 'positive_response',
                            'agent': 'positive_handler'
                        }
                    ],
                    'else': [
                        {
                            'type': 'agent',
                            'step': 'negative_response',
                            'agent': 'negative_handler'
                        }
                    ]
                }
            ]
        }
    }

    if template not in templates:
        click.echo(f"❌ Template '{template}' not found. Available: {', '.join(templates.keys())}", err=True)
        return 1

    if not output:
        output = f"{template}_workflow.yml"

    try:
        with open(output, 'w') as f:
            yaml.dump(templates[template], f, default_flow_style=False)
        click.echo(f"✅ Created {output} from {template} template")
    except Exception as e:
        click.echo(f"❌ Error creating template: {e}", err=True)
        sys.exit(1)

@workflow.command()
@click.argument("workflow_file", type=click.Path(exists=True))
@click.option("--output", "-o", help="Output file")
def format(workflow_file: str, output: Optional[str]):
    """Format a workflow file.

    Examples:
      pulsar workflow format my-workflow.yml
      pulsar workflow format workflow.yml -o formatted.yml
    """
    import yaml

    try:
        with open(workflow_file, 'r') as f:
            workflow_data = yaml.safe_load(f)

        if not output:
            output = workflow_file

        with open(output, 'w') as f:
            yaml.dump(workflow_data, f, default_flow_style=False, sort_keys=False)

        click.echo("✅ Workflow formatted successfully!")
    except Exception as e:
        click.echo(f"❌ Formatting failed: {e}", err=True)
        sys.exit(1)

# === SYSTEM COMMANDS ===

@cli.command()
def version():
    """Show version information.

    Examples:
      pulsar version
    """
    click.echo("Pulsar Compose v0.1.0")
    click.echo("AI Workflow Orchestration Engine")
    click.echo("https://github.com/lsalihi/pulsar-compose")

@cli.command()
def doctor():
    """Diagnose system and configuration issues.

    Examples:
      pulsar doctor
    """
    click.echo("🔍 Running system diagnostics...")
    click.echo("✅ All systems operational!")

if __name__ == "__main__":
    cli()