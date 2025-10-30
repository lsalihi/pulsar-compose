# Simple Chain Example

## Overview
The SIMPLE_CHAIN.yml workflow demonstrates basic sequential execution of AI agents in a content generation pipeline.

## Workflow Steps

1. **Idea Generation** - Creates 5 blog post ideas
2. **Outline Creation** - Develops detailed content structure
3. **Content Writing** - Produces final blog post

## Use Cases
- Content creation pipelines
- Sequential processing workflows
- Multi-step AI transformations

## Input Format
```
"artificial intelligence trends in 2025"
```

## Expected Output
- `blog_ideas`: List of 5 blog post concepts
- `blog_outline`: Structured content outline
- `final_content`: Complete blog post (800-1000 words)

## Running the Example
```bash
pulsar run examples/SIMPLE_CHAIN.yml --input "your topic here"
```

## Customization
- Modify agent models/providers in the `agents` section
- Adjust temperature and token limits for different creativity levels
- Add additional processing steps as needed