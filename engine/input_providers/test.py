"""
Test input provider for automated testing and predefined responses.
"""

import asyncio
from typing import Dict, List, Any, Optional

from .base import InputProvider, InteractionRequest, InteractionResponse, ValidationError


class TestInputProvider(InputProvider):
    """Input provider for automated testing with predefined responses."""
    # Prevent pytest from attempting to collect this as a test class
    __test__ = False

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.responses = config.get('responses', {}) if config else {}
        self.default_responses = config.get('default_responses', {}) if config else {}
        self.delay = config.get('delay', 0) if config else 0  # Simulated delay in seconds
        self.fail_on_missing = config.get('fail_on_missing', True) if config else True

    async def can_handle(self, request: InteractionRequest) -> bool:
        """Check if this provider can handle test interactions."""
        return True

    async def get_input(self, request: InteractionRequest) -> InteractionResponse:
        """Get predefined test input."""
        # Simulate delay if configured
        if self.delay > 0:
            await asyncio.sleep(self.delay)

        answers = {}

        # Try to get responses from config
        for i, question in enumerate(request.questions):
            question_key = f"question_{i}"

            # Check for specific response
            if question_key in self.responses:
                answers[question_key] = self.responses[question_key]
            elif str(i) in self.responses:
                answers[question_key] = self.responses[str(i)]
            elif question.question in self.responses:
                answers[question_key] = self.responses[question.question]
            # Check for default response
            elif question_key in self.default_responses:
                answers[question_key] = self.default_responses[question_key]
            elif str(i) in self.default_responses:
                answers[question_key] = self.default_responses[str(i)]
            elif question.question in self.default_responses:
                answers[question_key] = self.default_responses[question.question]
            # Use question default
            elif question.default is not None:
                answers[question_key] = question.default
            # Fail if no response found and configured to fail
            elif self.fail_on_missing:
                raise ValidationError(question.question, f"No test response configured for question {i}")
            else:
                # Provide sensible defaults
                answers[question_key] = self._get_sensible_default(question)

        response = InteractionResponse(
            answers=answers,
            metadata={
                'provider': 'test',
                'delay_used': self.delay,
                'responses_used': len(answers)
            }
        )

        # Validate the response
        self.validate_response(request, response)

        return response

    def _get_sensible_default(self, question) -> Any:
        """Get a sensible default value for testing."""
        if question.type.value == 'text':
            return f"Test answer for: {question.question[:20]}..."
        elif question.type.value == 'multiple_choice':
            if question.multiple:
                return question.options[:2] if question.options else ["test_option_1", "test_option_2"]
            else:
                return question.options[0] if question.options else "test_option"
        elif question.type.value == 'number':
            return 42
        elif question.type.value == 'boolean':
            return True
        else:
            return "test_default"

    def set_response(self, key: str, value: Any):
        """Set a test response for a specific key."""
        self.responses[key] = value

    def set_responses(self, responses: Dict[str, Any]):
        """Set multiple test responses."""
        self.responses.update(responses)

    def clear_responses(self):
        """Clear all test responses."""
        self.responses.clear()

    def add_scenario(self, name: str, responses: Dict[str, Any]):
        """Add a named test scenario."""
        if not hasattr(self, 'scenarios'):
            self.scenarios = {}
        self.scenarios[name] = responses

    def load_scenario(self, name: str):
        """Load a named test scenario."""
        if hasattr(self, 'scenarios') and name in self.scenarios:
            self.responses = self.scenarios[name].copy()
        else:
            raise ValueError(f"Test scenario '{name}' not found")

    @classmethod
    def create_with_responses(cls, responses: Dict[str, Any], **kwargs) -> 'TestInputProvider':
        """Create a test provider with predefined responses."""
        config = {'responses': responses, **kwargs}
        return cls(config)

    @classmethod
    def create_scenario(cls, scenario_name: str, responses: Dict[str, Any], **kwargs) -> 'TestInputProvider':
        """Create a test provider with a named scenario."""
        provider = cls({'responses': responses, **kwargs})
        provider.add_scenario(scenario_name, responses)
        return provider