"""
Interaction step handler for user input in workflows.
"""

import asyncio
from typing import TYPE_CHECKING, Dict, List, Any, Optional
from engine.step_handlers.base import BaseStepHandler
from engine.input_providers import InputProviderFactory, InteractionRequest, Question, QuestionType
from engine.results import StepResult

if TYPE_CHECKING:
    from models.state import StateManager
    from models.workflow import InteractionStep


class InteractionStepHandler(BaseStepHandler):
    """Handler for executing interaction steps that gather user input."""

    def __init__(self, state_manager: "StateManager", input_providers: Optional[Dict[str, Any]] = None):
        super().__init__(state_manager)
        self.input_providers = input_providers or {}
        self._setup_default_providers()

    def _setup_default_providers(self):
        """Set up default input providers."""
        from engine.input_providers import ConsoleInputProvider, WebInputProvider, FileInputProvider, TestInputProvider

        # Register default providers
        InputProviderFactory.register('console', ConsoleInputProvider)
        InputProviderFactory.register('web', WebInputProvider)
        InputProviderFactory.register('file', FileInputProvider)
        InputProviderFactory.register('test', TestInputProvider)

        # Add any configured providers
        for name, provider_config in self.input_providers.items():
            if isinstance(provider_config, dict) and 'class' in provider_config:
                # Dynamic provider loading (could be extended)
                pass

    async def can_handle(self, step) -> bool:
        """Check if step is an interaction step."""
        return hasattr(step, 'type') and step.type == "interaction"

    async def execute(self, step: "InteractionStep") -> StepResult:
        """Execute an interaction step."""
        try:
            # Parse the ask_user configuration
            questions = self._parse_questions(step.ask_user)

            # Create interaction request
            request = InteractionRequest(
                questions=questions,
                timeout=step.timeout,
                metadata={
                    'step_name': step.step,
                    'save_variable': step.save_to,
                    'title': step.ask_user.get('title', f'Input Required for {step.step}'),
                    'description': step.ask_user.get('description', '')
                }
            )

            # Get the input provider
            provider_name = step.provider or 'console'
            provider = InputProviderFactory.create(provider_name, self.input_providers.get(provider_name, {}))

            # Check if provider can handle the request
            if not await provider.can_handle(request):
                raise ValueError(f"Input provider '{provider_name}' cannot handle this request")

            # Get user input
            response = await provider.get_input(request)

            # Save responses to state
            await self.state_manager.set(step.save_to, response.answers)

            # Create success result
            return await self._create_step_result(
                step.step,
                success=True,
                output=response.answers,
                metadata={
                    'provider': provider_name,
                    'questions_count': len(questions),
                    'response_metadata': response.metadata
                }
            )

        except Exception as e:
            error_msg = f"Interaction failed: {str(e)}"
            return await self._create_step_result(
                step.step,
                success=False,
                error=error_msg,
                metadata={'error_type': type(e).__name__}
            )

    def _parse_questions(self, ask_user_config: Dict[str, Any]) -> List[Question]:
        """Parse the ask_user configuration into Question objects."""
        questions = []

        for question_config in ask_user_config.get('questions', []):
            question = Question(
                question=question_config['question'],
                type=self._parse_question_type(question_config.get('type', 'text')),
                required=question_config.get('required', True),
                default=question_config.get('default'),
                placeholder=question_config.get('placeholder'),
                options=question_config.get('options'),
                multiple=question_config.get('multiple', False),
                validation=question_config.get('validation')
            )
            questions.append(question)

        return questions

    def _parse_question_type(self, type_str: str) -> QuestionType:
        """Parse question type string to QuestionType enum."""
        type_mapping = {
            'text': QuestionType.TEXT,
            'multiple_choice': QuestionType.MULTIPLE_CHOICE,
            'number': QuestionType.NUMBER,
            'boolean': QuestionType.BOOLEAN
        }

        if type_str not in type_mapping:
            raise ValueError(f"Unknown question type: {type_str}")

        return type_mapping[type_str]