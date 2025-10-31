Workflow Fundamentals
====================

Workflows are the core of Pulsar - they define how AI agents collaborate to accomplish tasks.

Workflow Structure
------------------

A basic workflow consists of:

.. code-block:: yaml

   version: "0.1"
   name: "My Workflow"
   description: "What this workflow does"
   agents:      # AI agents available to the workflow
     # ... agent definitions
   workflow:    # Steps to execute
     # ... step definitions

Version
~~~~~~~

Workflow format version. Currently ``"0.1"``.

Name and Description
~~~~~~~~~~~~~~~~~~~~

Human-readable identifiers:

.. code-block:: yaml

   name: "Content Generation Pipeline"
   description: "Generate blog posts from research topics"

Agents
~~~~~~

Define AI models available to the workflow:

.. code-block:: yaml

   agents:
     researcher:
       model: "gpt-4"
       provider: "openai"
       prompt: "You are a research specialist"
       temperature: 0.7

     writer:
       model: "claude-3-sonnet-20240229"
       provider: "anthropic"
       prompt: "You are a creative writer"

Workflow Steps
~~~~~~~~~~~~~~

The sequence of operations:

.. code-block:: yaml

   workflow:
     - type: "agent"
       step: "research_topic"
       agent: "researcher"
       prompt: "Research: {{input}}"
       save_to: "research"

     - type: "agent"
       step: "write_article"
       agent: "writer"
       prompt: "Write article using: {{research}}"
       save_to: "article"

Step Types
----------

Agent Steps
~~~~~~~~~~~

Execute AI models:

.. code-block:: yaml

   - type: "agent"
       step: "my_step"
       agent: "agent_name"
       prompt: "What to do: {{input}}"
       save_to: "result"
       temperature: 0.8      # Optional
       max_tokens: 1000      # Optional
       timeout: 30          # Optional

Conditional Steps
~~~~~~~~~~~~~~~~~

Branch based on conditions:

.. code-block:: yaml

   - type: "conditional"
     step: "check_quality"
     if: "{{len(result) > 100}}"
     then:
       - type: "agent"
         step: "publish"
         agent: "publisher"
         prompt: "Publish: {{result}}"
     else:
       - type: "agent"
         step: "improve"
         agent: "editor"
         prompt: "Improve: {{result}}"

Interaction Steps
~~~~~~~~~~~~~~~~~

Get user input:

.. code-block:: yaml

   - type: "interaction"
     step: "get_feedback"
     ask_user:
       - question: "Rate the result (1-5)"
         type: "number"
         required: true
       - question: "Comments?"
         type: "text"
     save_to: "feedback"

Templates and Variables
-----------------------

Jinja2 templating enables dynamic content:

Global Variables
~~~~~~~~~~~~~~~~

.. code-block:: yaml

   variables:
     style: "professional"
     max_length: 500

   workflow:
     - type: "agent"
       step: "write"
       prompt: "Write a {{style}} summary under {{max_length}} characters"

Step Variables
~~~~~~~~~~~~~~

Access previous step outputs:

.. code-block:: yaml

   workflow:
     - type: "agent"
       step: "research"
       save_to: "research_data"

     - type: "agent"
       step: "summarize"
       prompt: "Summarize: {{research_data}}"

Built-in Functions
~~~~~~~~~~~~~~~~~~

Use functions in templates:

.. code-block:: yaml

   variables:
     items: ["apple", "banana", "cherry"]

   workflow:
     - type: "conditional"
       if: "{{len(items) > 2}}"
       then: [...]

Available functions:

- ``len(obj)`` - Length of string, list, or dict
- ``int(value)`` - Convert to integer
- ``float(value)`` - Convert to float
- ``str(value)`` - Convert to string
- ``bool(value)`` - Convert to boolean
- ``upper(text)`` - Uppercase string
- ``lower(text)`` - Lowercase string
- ``split(text, sep)`` - Split string
- ``join(items, sep)`` - Join list with separator

Advanced Features
-----------------

Error Handling
~~~~~~~~~~~~~~

Configure retry behavior:

.. code-block:: yaml

   workflow:
     - type: "agent"
       step: "unreliable_task"
       agent: "unreliable_agent"
       retry:
         attempts: 3
         backoff: 2.0  # Exponential backoff multiplier
         max_delay: 60  # Maximum delay between retries

Async Execution
~~~~~~~~~~~~~~~

Steps can run concurrently when independent:

.. code-block:: yaml

   workflow:
     - type: "agent"
       step: "task1"
       agent: "worker1"
       depends_on: []  # No dependencies

     - type: "agent"
       step: "task2"
       agent: "worker2"
       depends_on: []  # No dependencies

     - type: "agent"
       step: "combine"
       agent: "combiner"
       depends_on: ["task1", "task2"]  # Wait for both

State Management
~~~~~~~~~~~~~~~~

Access workflow execution state:

.. code-block:: yaml

   workflow:
     - type: "conditional"
       if: "{{state.step_count > 5}}"
       then: [...]

     - type: "agent"
       prompt: "Previous result: {{state.last_output}}"

Workflow Validation
-------------------

Pulsar validates workflows before execution:

.. code-block:: bash

   # Validate syntax and structure
   pulsar validate workflow.yml

   # Check agent references
   pulsar validate --strict workflow.yml

Common Issues
~~~~~~~~~~~~~

**Undefined Variables**

.. code-block:: text

   ERROR: Undefined variable 'missing_var'

Solution: Ensure all variables are defined before use.

**Circular Dependencies**

.. code-block:: text

   ERROR: Circular dependency detected

Solution: Reorder steps to avoid circular references.

**Invalid Agent Reference**

.. code-block:: text

   ERROR: Agent 'nonexistent' not found

Solution: Define all referenced agents in the ``agents`` section.

**Template Syntax Error**

.. code-block:: text

   ERROR: Template syntax error

Solution: Check Jinja2 template syntax in prompts and conditions.

Best Practices
--------------

**Structure**

- Use descriptive names for steps and agents
- Group related steps together
- Add comments for complex logic

**Performance**

- Use appropriate model sizes for tasks
- Set reasonable timeouts
- Configure retry policies

**Maintainability**

- Use variables for common values
- Create reusable agent configurations
- Document complex workflows

**Error Handling**

- Always configure retry policies for unreliable operations
- Use conditional steps for error recovery
- Log important state changes

Example Workflows
-----------------

See the ``examples/`` directory for complete workflows:

- ``simple_chain.yml`` - Basic agent chaining
- ``conditional_workflow.yml`` - Branching logic
- ``content_creation.yml`` - Multi-agent collaboration
- ``data_analysis.yml`` - Analytical workflows