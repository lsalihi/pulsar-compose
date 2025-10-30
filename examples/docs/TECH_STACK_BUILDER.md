# Tech Stack Builder Example

## Overview
The TECH_STACK_BUILDER.yml workflow demonstrates complex multi-agent collaboration for full-stack application development.

## Agent Roles

1. **Architect** - Designs system architecture and tech stack
2. **Backend Developer** - Implements API, database models, business logic
3. **Frontend Developer** - Creates UI components and client-side logic
4. **Database Specialist** - Designs schema, relationships, migrations
5. **Tester** - Writes comprehensive test suites
6. **DevOps Engineer** - Creates deployment and infrastructure config
7. **Documentation Writer** - Produces project documentation

## Workflow Flow
All agents work in parallel after initial architecture design, then documentation is created last.

## Use Cases
- Full-stack application development
- System architecture design
- Complete project scaffolding
- Multi-disciplinary team simulation

## Input Format
```
"e-commerce platform for handmade crafts"
```

## Expected Output
- `system_architecture`: Complete tech stack and architecture design
- `backend_code`: Full backend implementation
- `frontend_code`: Complete frontend application
- `database_schema`: Database design and migrations
- `test_suite`: Comprehensive test coverage
- `devops_config`: Deployment and infrastructure setup
- `documentation`: README, API docs, deployment guide

## Technology Stack Examples
The workflow can generate applications using:
- **Backend**: Node.js/Express, Python/FastAPI, Go/Gin
- **Frontend**: React, Vue.js, Angular, Svelte
- **Database**: PostgreSQL, MongoDB, MySQL
- **Deployment**: Docker, Kubernetes, AWS/GCP/Azure

## Running the Example
```bash
pulsar run examples/TECH_STACK_BUILDER.yml --input "your application idea"
```

## Customization
- Modify technology preferences in architect prompts
- Add specific framework requirements
- Include additional specialist roles (security, performance, etc.)
- Customize documentation templates