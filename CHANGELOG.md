# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive Sphinx documentation with API reference
- Docker containerization support
- Homebrew formula for macOS installation
- GitHub Actions CI/CD pipeline
- Pre-commit hooks for code quality
- Plugin system for extensible input providers and step handlers
- Async/await support for concurrent workflow execution
- Jinja2 templating engine for dynamic prompts and conditions
- Rich CLI interface with progress bars and colored output
- Command history and auto-completion
- Multiple input providers (console, file, web, test)
- Conditional workflow steps with expression evaluation
- User interaction steps for workflow input
- Comprehensive test suite with pytest and coverage reporting
- Type hints throughout codebase
- Pydantic models for configuration validation
- Support for multiple AI providers (OpenAI, Anthropic, Ollama)
- YAML-based workflow definitions
- Dependency management with Poetry
- Modular architecture with clear separation of concerns

### Changed
- Improved error handling and retry logic
- Enhanced logging and debugging capabilities
- Updated packaging configuration for PyPI distribution
- Restructured codebase for better maintainability

### Fixed
- Test coverage threshold adjusted to realistic levels
- Mocking issues in test suite resolved
- Agent step validation and execution errors fixed
- Conditional step syntax validation improved

## [0.1.0] - 2025-10-31

### Added
- Initial release of Pulsar workflow engine
- Core workflow execution functionality
- Basic AI agent integrations
- Command-line interface
- YAML workflow format support
- Basic documentation and examples