# Conditional Review Example

## Overview
The CONDITIONAL_REVIEW.yml workflow demonstrates quality-gated content creation with conditional branching and retry logic.

## Workflow Logic

1. **Content Generation** - Creates initial draft
2. **Quality Review** - Evaluates content quality (1-10 scale)
3. **Conditional Branching**:
   - Score > 7: Direct publishing
   - Score ≤ 7: Content improvement → Re-review → Publishing

## Key Features
- Quality assessment with numerical scoring
- Automatic content improvement for low-quality output
- Retry logic with different quality thresholds
- Fallback publishing for persistently low-quality content

## Use Cases
- Quality assurance pipelines
- Content moderation systems
- Automated review processes
- Iterative improvement workflows

## Input Format
```
"Write an article about renewable energy solutions"
```

## Expected Output
- `draft_content`: Initial content draft
- `quality_review`: Detailed quality assessment
- `published_content`: Final publish-ready content

## Quality Gates
- **Primary Gate**: Score > 7 for direct publishing
- **Secondary Gate**: Score > 6 after improvement
- **Fallback**: Publish with disclaimer if still low quality

## Running the Example
```bash
pulsar run examples/CONDITIONAL_REVIEW.yml --input "your content topic"
```

## Customization
- Adjust quality thresholds in conditional statements
- Modify review criteria in the quality_reviewer prompt
- Add additional improvement iterations
- Customize publishing formats