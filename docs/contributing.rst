Contributing Guide
=================

Welcome! We appreciate your interest in contributing to Pulsar. This guide will help you get started with development, testing, and contributing to the project.

Development Setup
=================

Prerequisites
-------------

- Python 3.9 or later
- Poetry (dependency management)
- Git

Clone and Setup
---------------

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/lsalihi/pulsar-compose.git
   cd pulsar-compose

   # Install dependencies
   poetry install

   # Install pre-commit hooks
   poetry run pre-commit install

   # Set up development environment
   poetry run python -m pytest --cov=. --cov-report=html

Project Structure
=================

.. code-block::

   pulsar/
   ├── agents/              # AI agent implementations
   │   ├── base.py         # Base agent interface
   │   ├── factory.py      # Agent creation factory
   │   ├── openai_agent.py # OpenAI integration
   │   ├── anthropic_agent.py  # Anthropic integration
   │   └── local_agent.py  # Ollama integration
   ├── cli/                # Command-line interface
   │   ├── main.py         # Main CLI entry point
   │   ├── config.py       # CLI configuration
   │   ├── history.py      # Command history
   │   ├── progress.py     # Progress tracking
   │   └── plugins.py      # Plugin system
   ├── engine/             # Core execution engine
   │   ├── executor.py     # Workflow execution
   │   ├── expression_evaluator.py  # Template evaluation
   │   └── results.py      # Result handling
   ├── input_providers/    # Input data providers
   │   ├── base.py         # Base provider interface
   │   ├── console.py      # Console input
   │   ├── file.py         # File input
   │   ├── web.py          # Web input
   │   └── test.py         # Test input
   ├── models/             # Data models
   │   ├── __init__.py
   │   ├── state.py        # Execution state
   │   └── template.py     # Template models
   ├── step_handlers/      # Workflow step handlers
   │   ├── base.py         # Base handler interface
   │   ├── agent_handler.py    # Agent step execution
   │   ├── condition_handler.py  # Conditional logic
   │   └── interaction_handler.py  # User interaction
   ├── tests/              # Test suite
   ├── docs/               # Documentation
   ├── examples/           # Example workflows
   └── pyproject.toml      # Project configuration

Development Workflow
===================

1. **Choose an Issue**

   - Check `Issues <https://github.com/lsalihi/pulsar-compose/issues>`_ for open tasks
   - Look for issues labeled ``good first issue`` or ``help wanted``
   - Comment on the issue to indicate you're working on it

2. **Create a Branch**

   .. code-block:: bash

      # Create and switch to a feature branch
      git checkout -b feature/your-feature-name

      # Or for bug fixes
      git checkout -b fix/issue-number-description

3. **Make Changes**

   - Write clear, focused commits
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

4. **Run Tests**

   .. code-block:: bash

      # Run all tests
      poetry run pytest

      # Run with coverage
      poetry run pytest --cov=. --cov-report=html

      # Run specific tests
      poetry run pytest tests/test_specific_module.py

5. **Update Documentation**

   - Update docstrings for any changed functions
   - Add examples for new features
   - Update the changelog

6. **Submit a Pull Request**

   - Push your branch to GitHub
   - Create a pull request with a clear description
   - Reference any related issues
   - Wait for review and address feedback

Code Style
==========

Python Style
------------

We follow `PEP 8 <https://pep8.org/>`_ with some modifications:

- Line length: 88 characters (Black default)
- Use type hints for function parameters and return values
- Use docstrings following Google style
- Use f-strings for string formatting

.. code-block:: python

   def process_workflow(
       workflow_path: Path,
       config: Optional[Dict[str, Any]] = None
   ) -> ExecutionResult:
       """Process a workflow file and return execution results.

       Args:
           workflow_path: Path to the workflow YAML file
           config: Optional configuration overrides

       Returns:
           ExecutionResult containing workflow outputs and metadata

       Raises:
           WorkflowError: If workflow execution fails
       """
       # Implementation here
       pass

Formatting
----------

We use automated formatting tools:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting

These run automatically via pre-commit hooks. You can also run them manually:

.. code-block:: bash

   # Format code
   poetry run black .

   # Sort imports
   poetry run isort .

   # Check for linting issues
   poetry run flake8 .

Type Checking
-------------

Use mypy for static type checking:

.. code-block:: bash

   # Run type checking
   poetry run mypy .

Testing
=======

Test Structure
--------------

Tests are organized to mirror the source code structure:

.. code-block::

   tests/
   ├── test_agents/
   │   ├── test_base.py
   │   ├── test_factory.py
   │   └── test_openai_agent.py
   ├── test_cli/
   ├── test_engine/
   ├── test_input_providers/
   └── test_step_handlers/

Writing Tests
-------------

- Use pytest as the testing framework
- Use descriptive test names: ``test_function_name_condition_expected_result``
- Use fixtures for common setup
- Mock external dependencies
- Test both success and failure cases

.. code-block:: python

   import pytest
   from unittest.mock import Mock, patch

   from agents.factory import AgentFactory

   class TestAgentFactory:
       def test_create_openai_agent_success(self):
           """Test successful OpenAI agent creation."""
           config = {
               "model": "gpt-3.5-turbo",
               "provider": "openai",
               "api_key": "test-key"
           }

           with patch("agents.openai_agent.OpenAI") as mock_openai:
               factory = AgentFactory()
               agent = factory.create_agent("test_agent", config)

               assert agent is not None
               mock_openai.assert_called_once()

       def test_create_agent_invalid_provider(self):
           """Test agent creation with invalid provider."""
           config = {"provider": "invalid"}

           factory = AgentFactory()

           with pytest.raises(ValueError, match="Unsupported provider"):
               factory.create_agent("test_agent", config)

Test Coverage
-------------

Maintain test coverage above 80%. Check coverage with:

.. code-block:: bash

   poetry run pytest --cov=. --cov-report=html --cov-fail-under=80

View the HTML coverage report in ``htmlcov/index.html``.

Documentation
=============

Documentation Standards
-----------------------

- Use Google-style docstrings
- Document all public functions, classes, and methods
- Include type hints
- Provide usage examples where helpful

.. code-block:: python

   class WorkflowExecutor:
       """Executes Pulsar workflows with dependency management.

       This class handles the parsing, validation, and execution of
       workflow definitions, managing step dependencies and results.

       Attributes:
           config: Workflow configuration dictionary
           state: Current execution state

       Example:
           >>> executor = WorkflowExecutor()
           >>> result = executor.execute("workflow.yml")
           >>> print(result.outputs)
       """

Building Documentation
----------------------

Build the documentation locally:

.. code-block:: bash

   # Install documentation dependencies
   poetry install --with docs

   # Build HTML documentation
   cd docs
   poetry run sphinx-build -b html . _build/html

   # View documentation
   open _build/html/index.html

Adding New Features
===================

Agent Providers
---------------

To add a new AI provider:

1. Create a new agent class inheriting from ``BaseAgent``
2. Implement the required methods
3. Add the provider to the factory
4. Add configuration validation
5. Write comprehensive tests

.. code-block:: python

   from agents.base import BaseAgent

   class NewProviderAgent(BaseAgent):
       def __init__(self, config: Dict[str, Any]):
           super().__init__(config)
           # Initialize provider-specific setup

       async def generate(
           self,
           prompt: str,
           **kwargs
       ) -> str:
           # Implement generation logic
           pass

Input Providers
---------------

To add a new input provider:

1. Create a class inheriting from ``BaseInputProvider``
2. Implement the ``collect`` method
3. Register the provider in the CLI
4. Add configuration options

.. code-block:: python

   from input_providers.base import BaseInputProvider

   class DatabaseProvider(BaseInputProvider):
       async def collect(self, config: Dict[str, Any]) -> Any:
           # Implement data collection from database
           pass

Step Handlers
-------------

To add a new step type:

1. Create a handler class inheriting from ``BaseStepHandler``
2. Implement the ``execute`` method
3. Add step type validation
4. Update the executor to use the new handler

.. code-block:: python

   from step_handlers.base import BaseStepHandler

   class LoopStepHandler(BaseStepHandler):
       async def execute(
           self,
           step_config: Dict[str, Any],
           context: ExecutionContext
       ) -> StepResult:
           # Implement loop logic
           pass

CLI Extensions
--------------

To add new CLI commands:

1. Create a command function
2. Add it to the CLI parser
3. Implement the command logic
4. Add help text and examples

.. code-block:: python

   import click

   @cli.command()
   @click.argument("workflow")
   @click.option("--output", "-o", help="Output file")
   def validate(workflow, output):
       """Validate a workflow file."""
       # Implementation here
       pass

Release Process
===============

Version Management
------------------

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Updating Version
----------------

Update version in ``pyproject.toml``:

.. code-block:: toml

   [tool.poetry]
   version = "0.2.0"

Release Checklist
-----------------

- [ ] Update version number
- [ ] Update changelog
- [ ] Run full test suite
- [ ] Build documentation
- ] Create git tag
- [ ] Publish to PyPI
- [ ] Create GitHub release
- [ ] Update documentation site

.. code-block:: bash

   # Tag the release
   git tag -a v0.2.0 -m "Release version 0.2.0"

   # Push tags
   git push origin v0.2.0

   # Publish to PyPI
   poetry publish --build

Changelog
=========

Keep a changelog following `Keep a Changelog <https://keepachangelog.com/>`_ format:

.. code-block:: markdown

   # Changelog

   All notable changes to this project will be documented in this file.

   The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
   and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

   ## [Unreleased]

   ### Added
   - New feature description

   ### Changed
   - Changed feature description

   ### Fixed
   - Bug fix description

   ## [0.1.0] - 2024-01-01

   ### Added
   - Initial release

Community Guidelines
===================

Code of Conduct
---------------

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn and contribute
- Maintain professional communication

Communication
-------------

- Use GitHub issues for bug reports and feature requests
- Use GitHub discussions for general questions
- Join our Discord/Slack for real-time discussion
- Follow the project on social media for updates

Recognition
-----------

Contributors are recognized in:

- GitHub contributor statistics
- CHANGELOG.md for significant contributions
- Project documentation
- Release notes

Getting Help
============

Need help getting started?

- **Documentation**: Check the docs at ``docs/``
- **Examples**: Look at workflows in ``examples/``
- **Issues**: Search existing GitHub issues
- **Discussions**: Ask questions in GitHub discussions
- **Community**: Join our community chat

We're here to help you contribute successfully!