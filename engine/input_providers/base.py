"""
Base input provider interface for user interactions.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass


class QuestionType(Enum):
    """Types of questions that can be asked."""
    TEXT = "text"
    MULTIPLE_CHOICE = "multiple_choice"
    NUMBER = "number"
    BOOLEAN = "boolean"


@dataclass
class Question:
    """Represents a single question to ask the user."""
    question: str
    type: QuestionType
    required: bool = True
    default: Any = None
    placeholder: Optional[str] = None
    options: Optional[List[str]] = None  # For multiple_choice
    multiple: bool = False  # For multiple_choice, allow multiple selections
    validation: Optional[Dict[str, Any]] = None  # Additional validation rules


@dataclass
class InteractionRequest:
    """Request for user interaction."""
    questions: List[Question]
    timeout: Optional[int] = None  # Timeout in seconds
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class InteractionResponse:
    """Response from user interaction."""
    answers: Dict[str, Any]  # question -> answer mapping
    metadata: Optional[Dict[str, Any]] = None


class ValidationError(Exception):
    """Raised when input validation fails."""
    def __init__(self, question: str, message: str):
        self.question = question
        self.message = message
        super().__init__(f"Validation failed for '{question}': {message}")


class InputProvider(ABC):
    """Abstract base class for input providers."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    async def can_handle(self, request: InteractionRequest) -> bool:
        """Check if this provider can handle the given request."""
        pass

    @abstractmethod
    async def get_input(self, request: InteractionRequest) -> InteractionResponse:
        """Get input from the user based on the request."""
        pass

    def validate_response(self, request: InteractionRequest, response: InteractionResponse) -> None:
        """Validate the response against the request requirements."""
        for i, question in enumerate(request.questions):
            question_key = f"question_{i}"
            answer = response.answers.get(question_key)

            # Check required fields
            if question.required and (answer is None or answer == ""):
                raise ValidationError(question.question, "This field is required")

            # Type-specific validation
            if question.type == QuestionType.MULTIPLE_CHOICE:
                if question.multiple:
                    if not isinstance(answer, list):
                        raise ValidationError(question.question, "Multiple selection expected")
                    for item in answer:
                        if item not in question.options:
                            raise ValidationError(question.question, f"Invalid option: {item}")
                else:
                    if answer not in question.options:
                        raise ValidationError(question.question, f"Invalid option: {answer}")

            elif question.type == QuestionType.NUMBER:
                try:
                    float(answer)
                except (ValueError, TypeError):
                    raise ValidationError(question.question, "Must be a valid number")

            elif question.type == QuestionType.BOOLEAN:
                if not isinstance(answer, bool):
                    raise ValidationError(question.question, "Must be true or false")

            # Custom validation rules
            if question.validation:
                self._apply_custom_validation(question, answer)

    def _apply_custom_validation(self, question: Question, answer: Any) -> None:
        """Apply custom validation rules."""
        validation = question.validation

        if 'min_length' in validation and isinstance(answer, str):
            if len(answer) < validation['min_length']:
                raise ValidationError(question.question, f"Minimum length is {validation['min_length']}")

        if 'max_length' in validation and isinstance(answer, str):
            if len(answer) > validation['max_length']:
                raise ValidationError(question.question, f"Maximum length is {validation['max_length']}")

        if 'pattern' in validation and isinstance(answer, str):
            import re
            if not re.match(validation['pattern'], answer):
                raise ValidationError(question.question, f"Does not match required pattern")

        if 'min' in validation and isinstance(answer, (int, float)):
            if answer < validation['min']:
                raise ValidationError(question.question, f"Must be at least {validation['min']}")

        if 'max' in validation and isinstance(answer, (int, float)):
            if answer > validation['max']:
                raise ValidationError(question.question, f"Must be at most {validation['max']}")


class InputProviderFactory:
    """Factory for creating input providers."""

    _providers = {}

    @classmethod
    def register(cls, name: str, provider_class):
        """Register an input provider class."""
        cls._providers[name] = provider_class

    @classmethod
    def create(cls, name: str, config: Optional[Dict[str, Any]] = None) -> InputProvider:
        """Create an input provider instance."""
        if name not in cls._providers:
            raise ValueError(f"Unknown input provider: {name}")
        return cls._providers[name](config)

    @classmethod
    def list_providers(cls) -> List[str]:
        """List available input providers."""
        return list(cls._providers.keys())