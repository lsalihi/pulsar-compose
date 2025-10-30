from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import print as rprint
from engine.results import ExecutionResult, StepResult

class ProgressDisplay:
    """Handles progress visualization for workflow execution."""

    def __init__(self):
        self.console = Console()
        self.progress: Optional[Progress] = None

    def start_execution(self, workflow_name: str, total_steps: int):
        """Start progress display for workflow execution."""
        if not self.progress:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=self.console
            )
            self.progress.start()

        self.task_id = self.progress.add_task(
            f"Executing {workflow_name}",
            total=total_steps
        )

    def update_step(self, step_name: str, success: bool):
        """Update progress for completed step."""
        if self.progress:
            status = "✓" if success else "✗"
            color = "green" if success else "red"
            self.progress.update(
                self.task_id,
                description=f"[{color}]{status} {step_name}[/{color}]",
                advance=1
            )

    def finish_execution(self, result: ExecutionResult):
        """Finish progress display and show summary."""
        if self.progress:
            self.progress.stop()
            self.progress = None

        # Show execution summary
        self._show_execution_summary(result)

    def show_error(self, message: str):
        """Display error message."""
        error_text = Text(message, style="bold red")
        self.console.print(Panel(error_text, title="Error", border_style="red"))

    def show_success(self, message: str):
        """Display success message."""
        success_text = Text(message, style="bold green")
        self.console.print(Panel(success_text, title="Success", border_style="green"))

    def show_warning(self, message: str):
        """Display warning message."""
        warning_text = Text(message, style="bold yellow")
        self.console.print(Panel(warning_text, title="Warning", border_style="yellow"))

    def show_execution_result(self, result: ExecutionResult):
        """Display detailed execution results."""
        table = Table(title=f"Execution Results: {result.workflow_name}")
        table.add_column("Step", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Duration", style="yellow")
        table.add_column("Output", style="white")

        for step_result in result.step_results:
            status = "✓" if step_result.success else "✗"
            status_style = "green" if step_result.success else "red"
            duration = ".2f"
            output_preview = str(step_result.output)[:50] + "..." if len(str(step_result.output)) > 50 else str(step_result.output)

            table.add_row(
                step_result.step_name,
                f"[{status_style}]{status}[/{status_style}]",
                duration,
                output_preview
            )

        self.console.print(table)

        # Show final state
        if result.final_state:
            state_table = Table(title="Final State")
            state_table.add_column("Key", style="cyan")
            state_table.add_column("Value", style="white")

            for key, value in result.final_state.items():
                value_str = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                state_table.add_row(key, value_str)

            self.console.print(state_table)

    def _show_execution_summary(self, result: ExecutionResult):
        """Show execution summary panel."""
        status = "Completed" if result.success else "Failed"
        status_style = "green" if result.success else "red"
        duration = ".2f"

        summary_text = f"""
Workflow: {result.workflow_name}
Status: [{status_style}]{status}[/{status_style}]
Duration: {duration}s
Steps: {len(result.step_results)}
Successful: {sum(1 for r in result.step_results if r.success)}
Failed: {sum(1 for r in result.step_results if not r.success)}
"""

        if not result.success and result.error:
            summary_text += f"\nError: {result.error}"

        panel = Panel(
            summary_text.strip(),
            title="Execution Summary",
            border_style=status_style
        )
        self.console.print(panel)