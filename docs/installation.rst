Installation
============

Pulsar supports multiple installation methods for different use cases.

System Requirements
-------------------

- **Python**: 3.9 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 500MB free space

Installation Methods
--------------------

PyPI (Recommended)
~~~~~~~~~~~~~~~~~~

Install from PyPI using pip:

.. code-block:: bash

   pip install pulsar-compose

For development or the latest features:

.. code-block:: bash

   pip install --upgrade pulsar-compose

Poetry
~~~~~~

If you use Poetry for dependency management:

.. code-block:: bash

   poetry add pulsar-compose

Docker
~~~~~~

Use the official Docker image:

.. code-block:: bash

   # Pull the image
   docker pull ghcr.io/lsalihi/pulsar-compose:latest

   # Run a workflow
   docker run --rm -v $(pwd):/workflows \
     ghcr.io/lsalihi/pulsar-compose:latest \
     pulsar run /workflows/my-workflow.yml

Homebrew (macOS)
~~~~~~~~~~~~~~~~

Install on macOS using Homebrew:

.. code-block:: bash

   brew install pulsar-compose

From Source
~~~~~~~~~~~

Clone and install from source:

.. code-block:: bash

   git clone https://github.com/lsalihi/pulsar-compose.git
   cd pulsar-compose
   pip install -e .

AI Provider Setup
-----------------

OpenAI
~~~~~~

1. Get an API key from `OpenAI Platform <https://platform.openai.com/api-keys>`_
2. Set the environment variable:

.. code-block:: bash

   export OPENAI_API_KEY="your-api-key-here"

Anthropic Claude
~~~~~~~~~~~~~~~~

1. Get an API key from `Anthropic Console <https://console.anthropic.com/>`_
2. Set the environment variable:

.. code-block:: bash

   export ANTHROPIC_API_KEY="your-api-key-here"

Local Models (Ollama)
~~~~~~~~~~~~~~~~~~~~~

1. Install Ollama:

.. code-block:: bash

   # macOS
   brew install ollama

   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh

   # Windows - download from https://ollama.ai/download

2. Start Ollama service:

.. code-block:: bash

   ollama serve

3. Pull models:

.. code-block:: bash

   ollama pull llama2          # General purpose
   ollama pull codellama       # Code generation
   ollama pull mistral         # Fast and capable

4. Configure Pulsar (optional):

.. code-block:: bash

   export OLLAMA_BASE_URL="http://localhost:11434"

Verification
------------

Verify your installation:

.. code-block:: bash

   # Check version
   pulsar --version

   # List available commands
   pulsar --help

   # Validate a workflow file
   pulsar validate examples/simple_chain.yml

Troubleshooting
---------------

Common installation issues:

**Python Version Error**

.. code-block:: text

   ERROR: Package 'pulsar-compose' requires a different Python version

Solution: Upgrade Python to 3.9+ or use a virtual environment with the correct version.

**Import Error**

.. code-block:: text

   ModuleNotFoundError: No module named 'pulsar'

Solution: Ensure Pulsar is installed and you're using the correct Python environment.

**API Key Error**

.. code-block:: text

   ERROR: OpenAI API key not found

Solution: Set the appropriate environment variables for your AI providers.

**Ollama Connection Error**

.. code-block:: text

   ERROR: Cannot connect to Ollama

Solution: Ensure Ollama is running with ``ollama serve`` and the correct base URL is set.

**Permission Error (Linux/macOS)**

.. code-block:: text

   Permission denied

Solution: Install with ``--user`` flag or use a virtual environment.

.. code-block:: bash

   pip install --user pulsar-compose

Development Installation
------------------------

For contributors and developers:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/lsalihi/pulsar-compose.git
   cd pulsar-compose

   # Install with development dependencies
   poetry install

   # Or with pip
   pip install -e ".[dev]"

   # Run tests
   pytest tests/

   # Build documentation
   cd docs && make html