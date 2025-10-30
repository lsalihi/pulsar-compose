"""
Console input provider for CLI interactions using rich prompts.
"""

import asyncio
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.table import Table

from .base import InputProvider, InteractionRequest, InteractionResponse, QuestionType, ValidationError


class ConsoleInputProvider(InputProvider):
    """Input provider for console/CLI interactions using rich prompts."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.console = Console()
        self.show_progress = config.get('show_progress', True) if config else True
        self.theme = config.get('theme', 'default') if config else 'default'

    async def can_handle(self, request: InteractionRequest) -> bool:
        """Check if this provider can handle console interactions."""
        # Console provider can handle any request
        return True

    async def get_input(self, request: InteractionRequest) -> InteractionResponse:
        """Get input from console using rich prompts."""
        self.console.clear()

        # Show header
        if request.metadata and 'title' in request.metadata:
            title = request.metadata['title']
            self.console.print(Panel.fit(f"[bold blue]{title}[/bold blue]", border_style="blue"))

        # Show description if provided
        if request.metadata and 'description' in request.metadata:
            self.console.print(f"[dim]{request.metadata['description']}[/dim]\n")

        answers = {}
        total_questions = len(request.questions)

        for i, question in enumerate(request.questions):
            if self.show_progress:
                self.console.print(f"[dim]Question {i + 1} of {total_questions}[/dim]")

            try:
                answer = await self._ask_question(question, i)
                answers[f"question_{i}"] = answer

                # Show confirmation
                if self.show_progress:
                    self.console.print("[green]✓[/green] Answer recorded\n")

            except KeyboardInterrupt:
                raise ValidationError(question.question, "Input cancelled by user")
            except Exception as e:
                raise ValidationError(question.question, f"Input error: {str(e)}")

        return InteractionResponse(
            answers=answers,
            metadata={'provider': 'console', 'completed_at': asyncio.get_event_loop().time()}
        )

    async def _ask_question(self, question, index: int):
        """Ask a single question and return the answer."""
        question_text = Text(question.question, style="bold cyan")
        self.console.print(question_text)

        # Show additional info
        if question.placeholder:
            self.console.print(f"[dim]{question.placeholder}[/dim]")

        if question.default is not None:
            default_str = str(question.default)
            if len(default_str) > 20:
                default_str = default_str[:17] + "..."
            self.console.print(f"[dim]Default: {default_str}[/dim]")

        # Handle different question types
        if question.type == QuestionType.TEXT:
            return await self._ask_text_question(question)

        elif question.type == QuestionType.MULTIPLE_CHOICE:
            return await self._ask_multiple_choice_question(question)

        elif question.type == QuestionType.NUMBER:
            return await self._ask_number_question(question)

        elif question.type == QuestionType.BOOLEAN:
            return await self._ask_boolean_question(question)

        else:
            raise ValidationError(question.question, f"Unsupported question type: {question.type}")

    async def _ask_text_question(self, question) -> str:
        """Ask a text input question."""
        default = question.default if question.default is not None else ""

        # Use asyncio.to_thread to run the synchronous rich prompt in a thread
        def get_text_input():
            return Prompt.ask(
                "",
                default=default,
                show_default=default != ""
            )

        return await asyncio.to_thread(get_text_input)

    async def _ask_multiple_choice_question(self, question):
        """Ask a multiple choice question."""
        if not question.options:
            raise ValidationError(question.question, "Multiple choice question must have options")

        # Display options
        table = Table(show_header=False, show_edge=False, pad_edge=False)
        for i, option in enumerate(question.options, 1):
            table.add_row(f"[bold]{i}[/bold]", option)

        self.console.print(table)
        self.console.print()

        if question.multiple:
            # Multiple selection
            def get_multiple_selection():
                selected_indices = []
                while True:
                    response = Prompt.ask(
                        "Enter option numbers (comma-separated, or 'done' to finish)",
                        default="done" if selected_indices else ""
                    ).strip()

                    if response.lower() == 'done':
                        break

                    try:
                        indices = [int(x.strip()) - 1 for x in response.split(',')]
                        for idx in indices:
                            if 0 <= idx < len(question.options):
                                if idx not in selected_indices:
                                    selected_indices.append(idx)
                                    self.console.print(f"[green]✓[/green] Selected: {question.options[idx]}")
                            else:
                                self.console.print(f"[red]Invalid option: {idx + 1}[/red]")
                    except ValueError:
                        self.console.print("[red]Please enter valid numbers separated by commas[/red]")

                return [question.options[i] for i in sorted(selected_indices)]

            return await asyncio.to_thread(get_multiple_selection)
        else:
            # Single selection
            def get_single_selection():
                while True:
                    try:
                        choice = IntPrompt.ask(
                            "Enter option number",
                            choices=[str(i) for i in range(1, len(question.options) + 1)]
                        )
                        return question.options[choice - 1]
                    except (ValueError, EOFError):
                        self.console.print("[red]Please enter a valid option number[/red]")

            return await asyncio.to_thread(get_single_selection)

    async def _ask_number_question(self, question):
        """Ask a number input question."""
        default = question.default if question.default is not None else None

        def get_number_input():
            if isinstance(default, float) or (question.validation and 'decimal' in question.validation):
                return FloatPrompt.ask("", default=default)
            else:
                return IntPrompt.ask("", default=default)

        return await asyncio.to_thread(get_number_input)

    async def _ask_boolean_question(self, question) -> bool:
        """Ask a boolean question."""
        default = question.default if question.default is not None else None

        def get_boolean_input():
            return Confirm.ask("", default=default)

        return await asyncio.to_thread(get_boolean_input)