"""
File input provider for reading responses from files.
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

from .base import InputProvider, InteractionRequest, InteractionResponse, ValidationError, QuestionType


class FileInputProvider(InputProvider):
    """Input provider that reads responses from files."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.input_dir = config.get('input_dir', './input_responses') if config else './input_responses'
        self.file_format = config.get('file_format', 'json') if config else 'json'  # json, yaml, or txt
        self.create_dir = config.get('create_dir', True) if config else True

        # Create input directory if it doesn't exist
        if self.create_dir:
            Path(self.input_dir).mkdir(parents=True, exist_ok=True)

    async def can_handle(self, request: InteractionRequest) -> bool:
        """Check if this provider can handle file-based input."""
        return True

    async def get_input(self, request: InteractionRequest) -> InteractionResponse:
        """Get input from a file."""
        # Generate filename based on request or use configured filename
        filename = self._generate_filename(request)
        filepath = os.path.join(self.input_dir, filename)

        print(f"Waiting for input file: {filepath}")
        print("Please create this file with your responses...")

        # Wait for file to exist
        while not os.path.exists(filepath):
            await asyncio.sleep(1)  # Check every second

        print(f"Found input file: {filepath}")

        # Read and parse the file
        try:
            answers = await self._read_input_file(filepath, request)

            response = InteractionResponse(
                answers=answers,
                metadata={
                    'provider': 'file',
                    'filepath': filepath,
                    'file_format': self.file_format
                }
            )

            # Validate the response
            self.validate_response(request, response)

            return response

        except Exception as e:
            raise ValidationError("file_input", f"Error reading input file: {str(e)}")

    def _generate_filename(self, request: InteractionRequest) -> str:
        """Generate filename for the input file."""
        # Use configured filename or generate based on request
        if self.config and 'filename' in self.config:
            return self.config['filename']

        # Generate based on request metadata
        if request.metadata and 'filename' in request.metadata:
            return request.metadata['filename']

        # Default filename with timestamp
        import time
        timestamp = int(time.time())
        return f"input_{timestamp}.{self.file_format}"

    async def _read_input_file(self, filepath: str, request: InteractionRequest) -> Dict[str, Any]:
        """Read and parse the input file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if self.file_format == 'json':
            return self._parse_json_input(content, request)
        elif self.file_format == 'yaml':
            return self._parse_yaml_input(content, request)
        elif self.file_format == 'txt':
            return self._parse_text_input(content, request)
        else:
            raise ValidationError("file_input", f"Unsupported file format: {self.file_format}")

    def _parse_json_input(self, content: str, request: InteractionRequest) -> Dict[str, Any]:
        """Parse JSON input file."""
        try:
            data = json.loads(content)
            answers = {}

            # Map JSON keys to question answers
            for i, question in enumerate(request.questions):
                question_key = f"question_{i}"

                # Try different possible keys
                possible_keys = [
                    question_key,
                    f"q{i}",
                    question.question.lower().replace(' ', '_').replace('?', ''),
                    str(i)
                ]

                answer = None
                for key in possible_keys:
                    if key in data:
                        answer = data[key]
                        break

                if answer is not None:
                    answers[question_key] = answer

            return answers

        except json.JSONDecodeError as e:
            raise ValidationError("file_input", f"Invalid JSON: {str(e)}")

    def _parse_yaml_input(self, content: str, request: InteractionRequest) -> Dict[str, Any]:
        """Parse YAML input file."""
        try:
            import yaml
            data = yaml.safe_load(content)
            # Use same logic as JSON parsing
            return self._parse_json_input(json.dumps(data), request)
        except ImportError:
            raise ValidationError("file_input", "PyYAML not installed for YAML support")
        except Exception as e:
            raise ValidationError("file_input", f"Invalid YAML: {str(e)}")

    def _parse_text_input(self, content: str, request: InteractionRequest) -> Dict[str, Any]:
        """Parse plain text input file."""
        lines = content.strip().split('\n')
        answers = {}

        for i, question in enumerate(request.questions):
            if i < len(lines):
                line = lines[i].strip()
                if line:  # Skip empty lines
                    question_key = f"question_{i}"
                    
                    # Convert to appropriate type based on question type
                    if question.type == QuestionType.BOOLEAN:
                        # Handle boolean conversion
                        if line.lower() in ('true', 'yes', '1', 'on'):
                            answers[question_key] = True
                        elif line.lower() in ('false', 'no', '0', 'off'):
                            answers[question_key] = False
                        else:
                            answers[question_key] = line  # type: ignore[assignment] # Keep as string if unclear
                    elif question.type == QuestionType.NUMBER:
                        # Try to convert to number
                        try:
                            # Try int first, then float
                            if '.' in line:
                                answers[question_key] = float(line)  # type: ignore[assignment]
                            else:
                                answers[question_key] = int(line)  # type: ignore[assignment]
                        except ValueError:
                            answers[question_key] = line  # type: ignore[assignment] # Keep as string if not a number
                    else:
                        answers[question_key] = line  # type: ignore[assignment]

        return answers

    async def write_template_file(self, request: InteractionRequest, filename: Optional[str] = None) -> str:
        """Write a template file for the user to fill out."""
        if filename is None:
            filename = self._generate_filename(request)

        filepath = os.path.join(self.input_dir, filename)

        if self.file_format == 'json':
            template = self._generate_json_template(request)
        elif self.file_format == 'yaml':
            template = self._generate_yaml_template(request)
        else:
            template = self._generate_text_template(request)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)

        return filepath

    def _generate_json_template(self, request: InteractionRequest) -> str:
        """Generate a JSON template for the user."""
        template = {}
        comments = []

        for i, question in enumerate(request.questions):
            key = f"question_{i}"
            template[key] = self._get_default_value(question)

            # Add comments for clarity
            comments.append(f"// {question.question}")
            if question.type.value == 'multiple_choice' and question.options is not None:
                comments.append(f"// Options: {', '.join(question.options)}")
            if question.placeholder:
                comments.append(f"// {question.placeholder}")

        # Create JSON with comments (not valid JSON, but helpful for users)
        result = "{\n"
        for i, (key, value) in enumerate(template.items()):
            comment_lines = []
            if i * 3 < len(comments):
                comment_lines = comments[i*3:(i+1)*3]

            for comment in comment_lines:
                result += f"  {comment}\n"

            if isinstance(value, str):
                result += f'  "{key}": "{value}"'
            else:
                result += f'  "{key}": {value}'

            if i < len(template) - 1:
                result += ','
            result += '\n'

        result += "}\n"
        return result

    def _generate_yaml_template(self, request: InteractionRequest) -> str:
        """Generate a YAML template for the user."""
        template = "# Fill out your responses below\n"
        template += "# Remove the # from lines you want to answer\n\n"

        for i, question in enumerate(request.questions):
            key = f"question_{i}"
            default = self._get_default_value(request.questions[i])

            template += f"# {request.questions[i].question}\n"
            if request.questions[i].type.value == 'multiple_choice' and request.questions[i].options is not None:
                options = request.questions[i].options
                template += f"# Options: {', '.join(options)}\n"  # type: ignore[arg-type]
            if request.questions[i].placeholder:
                template += f"# {request.questions[i].placeholder}\n"

            if isinstance(default, str):
                template += f'# {key}: "{default}"\n'
            else:
                template += f'# {key}: {default}\n'
            template += '\n'

        return template

    def _generate_text_template(self, request: InteractionRequest) -> str:
        """Generate a plain text template."""
        template = "Please provide your answers, one per line:\n\n"

        for i, question in enumerate(request.questions):
            template += f"{i + 1}. {question.question}\n"
            if question.type.value == 'multiple_choice' and question.options is not None:
                template += f"   Options: {', '.join(question.options)}\n"
            if question.placeholder:
                template += f"   {question.placeholder}\n"
            template += "\n"

        return template

    def _get_default_value(self, question) -> Any:
        """Get a default value for a question."""
        if question.default is not None:
            return question.default

        if question.type.value == 'text':
            return ""
        elif question.type.value == 'multiple_choice':
            return "" if not question.multiple else []
        elif question.type.value == 'number':
            return 0
        elif question.type.value == 'boolean':
            return False
        else:
            return ""