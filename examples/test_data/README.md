# Test Data for Pulsar Workflow Examples

This directory contains test inputs and validation data for workflow examples.

## Test Cases

### SIMPLE_CHAIN.yml Test
**Input:** "renewable energy solutions"
**Expected Outputs:**
- blog_ideas: Contains 5 distinct blog post ideas
- blog_outline: Structured outline with introduction, sections, conclusion
- final_content: Complete 800-1000 word blog post

### CONDITIONAL_REVIEW.yml Test
**Input:** "artificial intelligence ethics"
**Validation Checks:**
- draft_content: Initial article draft
- quality_review: Contains numerical score 1-10
- published_content: Final polished content

### TECH_STACK_BUILDER.yml Test
**Input:** "fitness tracking mobile app"
**Expected Components:**
- system_architecture: Tech stack recommendations
- backend_code: API endpoints and models
- frontend_code: UI components
- database_schema: Tables and relationships
- test_suite: Unit and integration tests
- devops_config: Docker/K8s configuration
- documentation: README and API docs

## Validation Scripts

### Basic Validation
```python
# Validate workflow loads correctly
from models.workflow import Workflow
workflow = Workflow.from_yaml('examples/SIMPLE_CHAIN.yml')
assert workflow.name == "Content Generation Chain"
assert len(workflow.agents) == 3
assert len(workflow.workflow) == 3
```

### Content Validation
```python
# Check output quality
def validate_simple_chain_output(result):
    assert 'blog_ideas' in result
    assert 'blog_outline' in result
    assert 'final_content' in result
    assert len(result['blog_ideas'].split('\n')) >= 5
    assert len(result['final_content']) > 1000
```

## Performance Benchmarks

### Expected Execution Times
- SIMPLE_CHAIN.yml: 30-60 seconds
- CONDITIONAL_REVIEW.yml: 45-90 seconds (varies with quality gates)
- TECH_STACK_BUILDER.yml: 2-4 minutes

### Token Usage Estimates
- SIMPLE_CHAIN.yml: ~5,000 tokens
- CONDITIONAL_REVIEW.yml: ~8,000 tokens
- TECH_STACK_BUILDER.yml: ~25,000 tokens

## Error Scenarios

### Test Invalid Workflows
```yaml
# This should fail validation
version: "0.1"
name: "Invalid Workflow"
agents:
  bad_agent:
    model: "invalid-model"
    provider: "invalid-provider"
workflow:
  - type: "invalid_type"
```

### Test Missing Dependencies
- Remove API keys and verify error handling
- Test with invalid agent references
- Verify template variable validation

## Integration Tests

### CLI Integration
```bash
# Test CLI commands
pulsar validate examples/SIMPLE_CHAIN.yml
pulsar run examples/SIMPLE_CHAIN.yml --input "test input"
pulsar logs
```

### API Integration
```python
# Test different providers
test_cases = [
    {"provider": "openai", "model": "gpt-4"},
    {"provider": "anthropic", "model": "claude-3-sonnet-20240229"},
    {"provider": "local", "model": "llama2"}
]
```

## Sample Test Inputs

### Content Generation
- "machine learning applications in healthcare"
- "sustainable urban development strategies"
- "cryptocurrency market trends 2025"

### Technical Projects
- "real-time chat application with WebSocket"
- "e-commerce platform with payment integration"
- "data visualization dashboard for sales analytics"

### Research Topics
- "impact of social media on mental health"
- "advances in quantum computing"
- "climate change adaptation strategies"

### Customer Support
- "My account login is not working"
- "How do I reset my password?"
- "I need to cancel my subscription"

### Code Review
- Python Flask API code
- React component code
- Database schema SQL

## Automated Testing

### Pytest Integration
```python
import pytest
from models.workflow import Workflow
from engine.executor import PulsarEngine

@pytest.mark.parametrize("workflow_file", [
    "examples/SIMPLE_CHAIN.yml",
    "examples/CONDITIONAL_REVIEW.yml",
    "examples/TECH_STACK_BUILDER.yml"
])
def test_workflow_validation(workflow_file):
    workflow = Workflow.from_yaml(workflow_file)
    assert workflow.version == "0.1"
    assert len(workflow.agents) > 0
    assert len(workflow.workflow) > 0
```

### Performance Testing
```python
import time

def test_execution_performance():
    start_time = time.time()
    result = PulsarEngine.execute_workflow(workflow, input_data)
    execution_time = time.time() - start_time
    assert execution_time < 300  # 5 minute timeout
    return result
```