Quick Start Guide
================

This guide will get you up and running with Pulsar in under 10 minutes.

Installation
------------

Install Pulsar using pip:

.. code-block:: bash

   pip install pulsar-compose

Or using Poetry:

.. code-block:: bash

   poetry add pulsar-compose

For local AI models, install Ollama:

.. code-block:: bash

   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh

   # Pull a model
   ollama pull llama2

Your First Workflow
-------------------

Create a file called ``hello_world.yml``:

.. code-block:: yaml

   version: "0.1"
   name: "Hello World Workflow"
   description: "A simple workflow that greets the user"

   agents:
     greeter:
       model: "gpt-4"
       provider: "openai"
       prompt: "You are a friendly assistant"

   workflow:
     - type: "agent"
       step: "greet"
       agent: "greeter"
       prompt: "Say hello to {{input}} in a creative way"
       save_to: "greeting"

Run the workflow:

.. code-block:: bash

   # Set your OpenAI API key
   export OPENAI_API_KEY="your-api-key-here"

   # Run the workflow
   pulsar run hello_world.yml --input "Alice"

You should see output like:

.. code-block::

   🚀 Starting workflow: Hello World Workflow
   📝 Step 1/1: greet
   ✅ Workflow completed successfully

   Results:
   greeting: "Hello Alice! 🌟 What a wonderful day to meet someone as amazing as you! How can I brighten your day today?"

Multi-Agent Workflow
--------------------

Create a more complex workflow with multiple agents:

.. code-block:: yaml

   version: "0.1"
   name: "Content Creation Pipeline"
   description: "Generate and improve content using multiple AI agents"

   agents:
     researcher:
       model: "gpt-4"
       provider: "openai"
       prompt: "You are a research specialist"

     writer:
       model: "claude-3-sonnet-20240229"
       provider: "anthropic"
       prompt: "You are a creative writer"

     editor:
       model: "gpt-4"
       provider: "openai"
       prompt: "You are an expert editor"

   workflow:
     - type: "agent"
       step: "research"
       agent: "researcher"
       prompt: "Research key facts about: {{input}}"
       save_to: "research"

     - type: "agent"
       step: "write"
       agent: "writer"
       prompt: "Write an engaging article using this research: {{research}}"
       save_to: "draft"

     - type: "agent"
       step: "edit"
       agent: "editor"
       prompt: "Edit and improve this article: {{draft}}"
       save_to: "final"

Run it:

.. code-block:: bash

   export OPENAI_API_KEY="your-openai-key"
   export ANTHROPIC_API_KEY="your-anthropic-key"

   pulsar run content_creation.yml --input "renewable energy"

Conditional Workflows
--------------------

Add decision-making to your workflows:

.. code-block:: yaml

   version: "0.1"
   name: "Smart Content Processor"
   description: "Process content with conditional logic"

   agents:
     analyzer:
       model: "gpt-4"
       provider: "openai"
       prompt: "You analyze content quality"

     improver:
       model: "claude-3-haiku-20240307"
       provider: "anthropic"
       prompt: "You improve content"

   workflow:
     - type: "agent"
       step: "analyze"
       agent: "analyzer"
       prompt: "Rate this content quality on a scale of 1-10: {{input}}"
       save_to: "quality_score"

     - type: "conditional"
       step: "check_quality"
       if: "{{int(quality_score) >= 7}}"
       then:
         - type: "agent"
           step: "publish"
           agent: "analyzer"
           prompt: "Content is good enough: {{input}}"
           save_to: "result"
       else:
         - type: "agent"
           step: "improve"
           agent: "improver"
           prompt: "Improve this content: {{input}}"
           save_to: "improved_content"
         - type: "agent"
           step: "final_review"
           agent: "analyzer"
           prompt: "Review the improved content: {{improved_content}}"
           save_to: "result"

Using Templates
---------------

Pulsar supports Jinja2 templating for dynamic content:

.. code-block:: yaml

   version: "0.1"
   name: "Template Example"
   description: "Using templates for dynamic content"

   variables:
     style: "professional"
     tone: "friendly"
     max_length: 500

   agents:
     writer:
       model: "gpt-4"
       provider: "openai"
       prompt: "You are a {{style}} writer with a {{tone}} tone"

   workflow:
     - type: "agent"
       step: "write"
       agent: "writer"
       prompt: |
         Write a {{style}} article about {{input}}.
         Keep it under {{max_length}} characters.
         Use a {{tone}} tone throughout.
       save_to: "article"

Run with custom variables:

.. code-block:: bash

   pulsar run template_example.yml --input "artificial intelligence" --var style=creative --var tone=enthusiastic

Local AI Models
---------------

Use local models with Ollama for privacy and cost savings:

.. code-block:: yaml

   version: "0.1"
   name: "Local AI Workflow"
   description: "Using local Ollama models"

   agents:
     local_assistant:
       model: "llama2"
       provider: "local"
       prompt: "You are a helpful local AI assistant"

   workflow:
     - type: "agent"
       step: "assist"
       agent: "local_assistant"
       prompt: "Help with: {{input}}"
       save_to: "response"

Make sure Ollama is running:

.. code-block:: bash

   # Start Ollama service
   ollama serve

   # Run the workflow
   pulsar run local_workflow.yml --input "explain quantum computing"

Next Steps
----------

Now that you have the basics, explore:

- :doc:`../user_guide/workflows` - Advanced workflow patterns
- :doc:`../user_guide/agents` - AI provider configuration
- :doc:`../user_guide/templates` - Template system details
- :doc:`../user_guide/examples` - More example workflows

For API usage, see the :doc:`../api/index`.