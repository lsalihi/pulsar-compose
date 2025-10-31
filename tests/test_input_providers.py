"""
Comprehensive tests for the user interaction system.
"""

import pytest
import asyncio
import tempfile
import os
import json
from unittest.mock import patch, MagicMock

from engine.input_providers import (
    InputProviderFactory,
    ConsoleInputProvider,
    WebInputProvider,
    FileInputProvider,
    TestInputProvider,
    InteractionRequest,
    InteractionResponse,
    Question,
    QuestionType,
    ValidationError
)


class TestInputProviders:
    """Test suite for input providers."""

    @pytest.fixture
    def sample_questions(self):
        """Sample questions for testing."""
        return [
            Question(
                question="What's your name?",
                type=QuestionType.TEXT,
                required=True
            ),
            Question(
                question="Choose a framework",
                type=QuestionType.MULTIPLE_CHOICE,
                options=["React", "Vue", "Angular"],
                required=True
            ),
            Question(
                question="How many years experience?",
                type=QuestionType.NUMBER,
                validation={"min": 0, "max": 50}
            ),
            Question(
                question="Do you need help?",
                type=QuestionType.BOOLEAN,
                default=False
            )
        ]

    @pytest.fixture
    def sample_request(self, sample_questions):
        """Sample interaction request."""
        return InteractionRequest(
            questions=sample_questions,
            timeout=30,
            metadata={"title": "Test Survey", "description": "A test survey"}
        )

    def test_input_provider_factory(self):
        """Test input provider factory registration and creation."""
        # Test registration
        InputProviderFactory.register('test_provider', TestInputProvider)

        # Test creation
        provider = InputProviderFactory.create('test_provider')
        assert isinstance(provider, TestInputProvider)

        # Test unknown provider
        with pytest.raises(ValueError, match="Unknown input provider"):
            InputProviderFactory.create('unknown_provider')

    @pytest.mark.asyncio
    async def test_test_input_provider(self, sample_request):
        """Test the test input provider."""
        # Configure responses
        responses = {
            "question_0": "John Doe",
            "question_1": "React",
            "question_2": 5,
            "question_3": True
        }

        provider = TestInputProvider.create_with_responses(responses)

        response = await provider.get_input(sample_request)

        assert response.answers["question_0"] == "John Doe"
        assert response.answers["question_1"] == "React"
        assert response.answers["question_2"] == 5
        assert response.answers["question_3"] == True

    @pytest.mark.asyncio
    async def test_test_input_provider_defaults(self, sample_request):
        """Test test provider with defaults."""
        provider = TestInputProvider({'fail_on_missing': False})

        response = await provider.get_input(sample_request)

        # Should have sensible defaults
        assert "question_0" in response.answers
        assert "question_1" in response.answers
        assert isinstance(response.answers["question_2"], (int, float))
        assert isinstance(response.answers["question_3"], bool)

    @pytest.mark.asyncio
    async def test_file_input_provider_json(self, sample_request, tmp_path):
        """Test file input provider with JSON format."""
        # Create input file
        input_file = tmp_path / "input.json"
        input_data = {
            "question_0": "Jane Smith",
            "question_1": "Vue",
            "question_2": 10,
            "question_3": False
        }

        with open(input_file, 'w') as f:
            json.dump(input_data, f)

        provider = FileInputProvider({
            'input_dir': str(tmp_path),
            'file_format': 'json',
            'filename': 'input.json'  # Specify the filename
        })

        # File already exists, so no need to wait
        response = await provider.get_input(sample_request)

        assert response.answers["question_0"] == "Jane Smith"
        assert response.answers["question_1"] == "Vue"

    @pytest.mark.asyncio
    async def test_file_input_provider_text(self, sample_request, tmp_path):
        """Test file input provider with text format."""
        # Create input file
        input_file = tmp_path / "input.txt"
        input_content = "Alice Johnson\nAngular\n15\ntrue\n"

        with open(input_file, 'w') as f:
            f.write(input_content)

        provider = FileInputProvider({
            'input_dir': str(tmp_path),
            'file_format': 'txt',
            'filename': 'input.txt'  # Specify the filename
        })

        # File already exists, so no need to wait
        response = await provider.get_input(sample_request)

        assert response.answers["question_0"] == "Alice Johnson"
        assert response.answers["question_1"] == "Angular"

    @pytest.mark.asyncio
    async def test_console_input_provider_validation(self, sample_request):
        """Test console provider validation."""
        provider = ConsoleInputProvider()

        # Test validation
        valid_response = InteractionResponse(answers={
            "question_0": "Test User",
            "question_1": "React",
            "question_2": 25,
            "question_3": True
        })

        # Should not raise
        provider.validate_response(sample_request, valid_response)

        # Test invalid multiple choice
        invalid_response = InteractionResponse(answers={
            "question_0": "Test User",
            "question_1": "Invalid Choice",
            "question_2": 25,
            "question_3": True
        })

        with pytest.raises(ValidationError, match="Invalid option"):
            provider.validate_response(sample_request, invalid_response)

        # Test missing required field
        missing_required = InteractionResponse(answers={
            "question_1": "React",
            "question_2": 25,
            "question_3": True
        })

        with pytest.raises(ValidationError, match="required"):
            provider.validate_response(sample_request, missing_required)

    def test_validation_custom_rules(self):
        """Test custom validation rules."""
        question = Question(
            question="Enter text",
            type=QuestionType.TEXT,
            validation={
                "min_length": 5,
                "max_length": 10,
                "pattern": r"^[A-Za-z]+$"
            }
        )

        provider = ConsoleInputProvider()

        # Valid input
        valid_response = InteractionResponse(answers={"question_0": "Hello"})
        provider.validate_response(
            InteractionRequest(questions=[question]),
            valid_response
        )

        # Too short
        with pytest.raises(ValidationError, match="Minimum length"):
            invalid_response = InteractionResponse(answers={"question_0": "Hi"})
            provider.validate_response(
                InteractionRequest(questions=[question]),
                invalid_response
            )

        # Invalid pattern
        with pytest.raises(ValidationError, match="Does not match"):
            invalid_response = InteractionResponse(answers={"question_0": "Hello123"})
            provider.validate_response(
                InteractionRequest(questions=[question]),
                invalid_response
            )

    @pytest.mark.asyncio
    async def test_web_input_provider_creation(self):
        """Test web input provider initialization."""
        provider = WebInputProvider({
            'host': '127.0.0.1',
            'port': 9090,
            'base_url': 'http://127.0.0.1:9090'
        })

        assert provider.host == '127.0.0.1'
        assert provider.port == 9090
        assert await provider.can_handle(InteractionRequest(questions=[]))

    def test_question_types(self):
        """Test question type parsing."""
        # Test all question types
        text_q = Question(question="Text?", type=QuestionType.TEXT)
        choice_q = Question(question="Choice?", type=QuestionType.MULTIPLE_CHOICE, options=["A", "B"])
        number_q = Question(question="Number?", type=QuestionType.NUMBER)
        bool_q = Question(question="Bool?", type=QuestionType.BOOLEAN)

        assert text_q.type == QuestionType.TEXT
        assert choice_q.type == QuestionType.MULTIPLE_CHOICE
        assert number_q.type == QuestionType.NUMBER
        assert bool_q.type == QuestionType.BOOLEAN

    def test_provider_configuration(self):
        """Test provider configuration handling."""
        config = {
            'theme': 'dark',
            'show_progress': False,
            'timeout': 60
        }

        provider = ConsoleInputProvider(config)
        assert provider.config == config
        assert provider.theme == 'dark'