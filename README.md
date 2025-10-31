# Pulsar Workflow Engine v0.1

A declarative workflow engine for orchestrating AI agents in YAML-defined workflows. Supports multi-provider AI models with conditional logic, template rendering, and async execution.

## Features

- **YAML-based Workflows**: Define complex AI agent orchestrations using simple YAML syntax
- **Multi-Provider Support**: OpenAI, Anthropic Claude, and local Ollama models
- **Conditional Branching**: Dynamic workflow paths based on agent responses
- **Template Rendering**: Jinja2-based variable substitution and dynamic prompts
- **Async Execution**: Concurrent agent execution with progress tracking
- **State Management**: Dot-notation access with history tracking
- **CLI Interface**: Rich terminal UI with history, validation, and status commands
- **Plugin System**: Extensible architecture for custom step handlers
- **Error Handling**: Comprehensive retry logic with exponential backoff

## Installation

### 🚀 Recommended: Standalone Executable
**No dependencies required - download and run:**

```bash
# Or use the one-line installer (Linux/macOS):
curl -fsSL https://raw.githubusercontent.com/lsalihi/pulsar-compose/master/install.sh | bash

# Manual download
# Linux x64
wget https://github.com/lsalihi/pulsar-compose/releases/latest/download/pulsar-linux-x64
chmod +x pulsar-linux-x64 && sudo mv pulsar-linux-x64 /usr/local/bin/pulsar

# macOS (Intel/Apple Silicon)
wget https://github.com/lsalihi/pulsar-compose/releases/latest/download/pulsar-macos-$(uname -m)
chmod +x pulsar-macos-* && sudo mv pulsar-macos-* /usr/local/bin/pulsar

# Windows (PowerShell)
irm https://github.com/lsalihi/pulsar-compose/releases/latest/download/pulsar-windows-x64.exe -OutFile pulsar.exe
```

### 🐳 Docker Container
**Run without installation:**

```bash
# Docker Hub: https://hub.docker.com/r/lsalihi/pulsar-compose

# Quick start
docker run --rm lsalihi/pulsar-compose:latest --help

# With your workflows
docker run -v $(pwd):/workflows --rm lsalihi/pulsar-compose:latest run /workflows/my-workflow.yml

# Docker Compose style
docker run -v $(pwd):/workflows --rm lsalihi/pulsar-compose:latest compose up

# Persistent configuration
docker run -v $(pwd):/workflows -v ~/.pulsar:/root/.pulsar --rm lsalihi/pulsar-compose:latest
```

### 📦 Package Managers
**Install using your favorite package manager:**

```bash
# Homebrew (macOS/Linux)
brew install lsalihi/pulsar-compose/pulsar-compose

# PyPI (Python 3.9+ required)
pip install pulsar-compose

# Snap (Linux)
sudo snap install pulsar-compose

# Chocolatey (Windows)
choco install pulsar-compose

# Nix (Linux/macOS)
nix-env -iA nixpkgs.pulsar-compose
```

### 🔨 From Source
**For development or custom builds:**

```bash
git clone https://github.com/lsalihi/pulsar-compose.git
cd pulsar-compose
poetry install  # or: pip install -e .
poetry run pulsar --help
```

### ⚡ Verification
**After installation, verify it works:**

```bash
pulsar --version
pulsar --help
```

## Quick Start

### 1. Create a Simple Workflow

Create `examples/simple_chain.yml`:

```yaml
version: "0.1"
name: "Simple AI Chain"
description: "A basic workflow with two AI agents"

steps:
  - name: "analyze"
    type: "agent"
    agent:
      provider: "local"
      model: "llama2"
      prompt: "Analyze this topic: {{input}}"
    output: "analysis"

  - name: "summarize"
    type: "agent"
    agent:
      provider: "local"
      model: "llama2"
      prompt: "Summarize this analysis: {{analysis}}"
    output: "summary"
```

### 2. Run the Workflow

```bash
# Validate the workflow
pulsar validate examples/simple_chain.yml

# Execute with input
pulsar run examples/simple_chain.yml --input "artificial intelligence"

# View execution history
pulsar logs

# Check status
pulsar status
```

## Workflow Specification

### Basic Structure

```yaml
version: "0.1"
name: "My Workflow"
description: "Workflow description"
variables:  # Optional global variables
  temperature: 0.7
steps:
  - name: "step1"
    type: "agent"
    # ... step configuration
```

### Step Types

#### Agent Steps

Execute AI models with custom prompts:

```yaml
- name: "generate_ideas"
  type: "agent"
  agent:
    provider: "openai"  # or "anthropic" or "local"
    model: "gpt-4"      # provider-specific model name
    prompt: "Generate ideas for: {{input}}"
    temperature: 0.8   # optional
    max_tokens: 1000   # optional
  output: "ideas"       # variable to store result
```

#### Conditional Steps

Branch workflow based on conditions:

```yaml
- name: "check_quality"
  type: "condition"
  condition: "{{len(ideas.split()) > 10}}"
  then: "high_quality"
  else: "low_quality"
```

### Variables and Templates

Use Jinja2 templating for dynamic content:

```yaml
variables:
  system_prompt: "You are a helpful assistant"
  user_name: "Alice"

steps:
  - name: "greet"
    type: "agent"
    agent:
      provider: "local"
      model: "llama2"
      prompt: |
        {{system_prompt}}

        Hello {{user_name}}, how can I help you today?
```

### State Access

Access workflow state using dot notation:

```yaml
# Access nested data
condition: "{{results.agent1.score > 0.8}}"

# Access lists
condition: "{{len(history.steps) > 5}}"

# Access previous outputs
prompt: "Previous result: {{previous_step.output}}"
```

## Configuration

### Environment Variables

Set API keys and configuration:

```bash
# OpenAI
export OPENAI_API_KEY="your-key-here"

# Anthropic
export ANTHROPIC_API_KEY="your-key-here"

# Ollama (local)
export OLLAMA_BASE_URL="http://localhost:11434"
```

### CLI Configuration

The CLI supports various commands:

```bash
# Initialize a new workflow
pulsar workflow init my-workflow.yml

# List available workflows
pulsar workflow list

# Run with custom variables
pulsar run workflow.yml --var temperature=0.9 --var model=gpt-4

# Get help
pulsar --help
```

## Advanced Features

### Error Handling

Built-in retry logic with exponential backoff:

```yaml
steps:
  - name: "unreliable_agent"
    type: "agent"
    agent:
      provider: "openai"
      model: "gpt-4"
      prompt: "Process: {{input}}"
    retry:
      attempts: 3
      backoff: 2.0
    output: "result"
```

### Async Execution

Steps can run concurrently when independent:

```yaml
steps:
  - name: "parallel_task_1"
    type: "agent"
    # ... config
    depends_on: []  # No dependencies

  - name: "parallel_task_2"
    type: "agent"
    # ... config
    depends_on: []  # No dependencies

  - name: "combine_results"
    type: "agent"
    depends_on: ["parallel_task_1", "parallel_task_2"]
    # ... combine the results
```

### Plugin System

Extend functionality with custom step handlers:

```python
from step_handlers.base import BaseStepHandler

class CustomHandler(BaseStepHandler):
    async def execute(self, step, state, context):
        # Custom logic here
        pass
```

## Examples

See the `examples/` directory for complete workflows:

- `simple_chain.yml`: Basic agent chaining
- `conditional_workflow.yml`: Branching logic example

## Development

### Running Tests

```bash
# Unit tests
poetry run pytest tests/ -v

# Integration tests (requires Ollama)
poetry run python test_ollama.py
```

### Project Structure

```
pulsar-compose/
├── models/           # Pydantic models and validation
├── agents/           # AI provider implementations
├── engine/           # Workflow execution engine
├── step_handlers/    # Step type handlers
├── cli/              # Command-line interface
├── tests/            # Unit and integration tests
└── examples/         # Sample workflows
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Check the examples in `examples/`
- Review the test files for usage patterns
- Open an issue on GitHub