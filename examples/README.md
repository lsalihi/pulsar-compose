# Pulsar Workflow Examples

This directory contains comprehensive examples demonstrating Pulsar's capabilities across various domains and use cases.

## Available Examples

### Core Workflow Patterns

1. **[SIMPLE_CHAIN.yml](SIMPLE_CHAIN.yml)** - Basic sequential execution
   - Content generation pipeline
   - 3-step linear workflow
   - Template variable usage

2. **[CONDITIONAL_REVIEW.yml](CONDITIONAL_REVIEW.yml)** - Quality-gated processing
   - Conditional branching logic
   - Retry mechanisms
   - Quality assessment workflows

3. **[TECH_STACK_BUILDER.yml](TECH_STACK_BUILDER.yml)** - Complex multi-agent collaboration
   - Full-stack application development
   - 7 specialized AI agents
   - Parallel processing

### Domain-Specific Workflows

4. **[RESEARCH_ANALYSIS.yml](RESEARCH_ANALYSIS.yml)** - Research and analysis pipeline
   - Data collection and analysis
   - Expert review integration
   - Report generation

5. **[CUSTOMER_SUPPORT.yml](CUSTOMER_SUPPORT.yml)** - Customer support automation
   - Ticket classification and routing
   - Sentiment analysis
   - Automated response generation

6. **[CODE_REVIEW.yml](CODE_REVIEW.yml)** - Code review and improvement
   - Security, performance, and quality analysis
   - Automated refactoring suggestions
   - Critical issue prioritization

7. **[DATA_ANALYSIS.yml](DATA_ANALYSIS.yml)** - Data analysis pipeline
   - Statistical analysis and visualization
   - Machine learning recommendations
   - Comprehensive reporting

8. **[CREATIVE_WRITING.yml](CREATIVE_WRITING.yml)** - Creative writing assistant
   - Story development and character design
   - Collaborative editing process
   - Style analysis and improvement

9. **[USER_INTERACTION.yml](USER_INTERACTION.yml)** - Dynamic user interaction demo
   - Interactive preference collection
   - Multiple input providers (console, web, file)
   - Real-time workflow adaptation

## User Interaction System

Pulsar supports dynamic user interaction through multiple input providers:

### Input Providers

- **Console Provider**: Rich CLI prompts with validation
- **Web Provider**: HTTP API for UI integration
- **File Provider**: Read responses from JSON/text files
- **Test Provider**: Automated testing and predefined responses

### Question Types

- **Text**: Free-form text input with validation
- **Multiple Choice**: Single or multiple selections from options
- **Number**: Numeric input with range validation
- **Boolean**: Yes/no questions

### Example Interaction Step
```yaml
- name: "user_input"
  type: "interaction"
  provider: "console"
  questions:
    - question: "What's your project type?"
      type: "multiple_choice"
      options: ["Web App", "API", "CLI Tool"]
      required: true
    - question: "Describe your requirements"
      type: "text"
      placeholder: "Detailed description..."
  save_to: "user_prefs"
```

### Using Responses
```yaml
- name: "process_input"
  type: "agent"
  prompt: "Based on user preferences: {{user_prefs}}"
```

## Template Files

The `templates/` directory contains reusable workflow templates:

- **basic_sequential.yml** - Simple linear workflow template
- **conditional_branching.yml** - Template with conditional logic
- **multi_agent_collaboration.yml** - Complex multi-agent template

## Running Examples

### Validate a Workflow
```bash
pulsar validate examples/SIMPLE_CHAIN.yml
```

### Execute a Workflow
```bash
pulsar run examples/SIMPLE_CHAIN.yml --input "your input here"
```

### View Execution History
```bash
pulsar logs
```

## Example Input/Output

### Simple Chain Example
**Input:** `"artificial intelligence in healthcare"`
**Output:** Complete blog post with ideas, outline, and full content

### Conditional Review Example
**Input:** `"Write about climate change solutions"`
**Output:** Quality-assessed content with potential revisions

### Tech Stack Builder Example
**Input:** `"task management application"`
**Output:** Complete application architecture, code, tests, and documentation

## Customization Guide

### Modifying Agent Configurations
```yaml
agents:
  my_agent:
    model: "gpt-4"                    # Change model
    provider: "openai"               # Change provider
    prompt: "Your custom prompt"     # Modify prompt
    parameters:
      temperature: 0.8              # Adjust creativity
      max_tokens: 1000              # Set response length
```

### Adding Conditional Logic
```yaml
- type: conditional
  step: "decision_point"
  if: "{{previous_step.output | regex_search(r'score: (\d+)') | int > 7}}"
  then:
    - # High quality path
  else:
    - # Low quality path
```

### Template Variables
- `{{input}}` - Original workflow input
- `{{step_name.output}}` - Output from previous steps
- `{{variable_name}}` - Custom variables

## Best Practices

1. **Start Simple** - Use basic templates for initial workflows
2. **Test Incrementally** - Validate each workflow before production use
3. **Monitor Costs** - Track token usage across different models
4. **Handle Errors** - Implement appropriate retry logic
5. **Version Control** - Keep workflow versions for reproducibility

## Troubleshooting

### Common Issues
- **Import Errors**: Ensure absolute imports in workflow files
- **Template Errors**: Check variable references and syntax
- **API Limits**: Monitor rate limits for different providers
- **Memory Issues**: Large contexts may exceed token limits

### Debug Mode
```bash
pulsar run workflow.yml --input "test" --verbose
```

## Contributing

To add new examples:
1. Create workflow YAML file
2. Add corresponding documentation
3. Test with multiple inputs
4. Update this README

## Performance Notes

- **Sequential Workflows**: Fastest, predictable execution
- **Conditional Workflows**: Variable execution time based on conditions
- **Multi-Agent Workflows**: Highest token usage, most comprehensive results
- **Local Models**: Lower cost, may be slower than cloud APIs