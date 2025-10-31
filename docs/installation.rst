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

Standalone Executable (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**No dependencies required - download and run:**

.. code-block:: bash

   # One-line installer (Linux/macOS)
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

Docker Container
~~~~~~~~~~~~~~~~

**Run without installation using Docker:**

.. code-block:: bash

   # Pull from GitHub Container Registry
   docker pull ghcr.io/lsalihi/pulsar-compose:latest

   # Quick start
   docker run --rm ghcr.io/lsalihi/pulsar-compose:latest --help

   # Run a workflow with your files
   docker run -v $(pwd):/workflows --rm ghcr.io/lsalihi/pulsar-compose:latest \
     run /workflows/my-workflow.yml --input "Hello world"

   # Docker Compose style commands
   docker run -v $(pwd):/workflows --rm ghcr.io/lsalihi/pulsar-compose:latest \
     compose up

   # With persistent configuration
   docker run -v $(pwd):/workflows -v ~/.pulsar:/root/.pulsar --rm \
     ghcr.io/lsalihi/pulsar-compose:latest

Package Managers
~~~~~~~~~~~~~~~~~

**Install using your favorite package manager:**

Homebrew (macOS/Linux):

.. code-block:: bash

   brew install lsalihi/pulsar-compose/pulsar-compose

PyPI (Python 3.9+ required):

.. code-block:: bash

   pip install pulsar-compose

Snap (Linux):

.. code-block:: bash

   sudo snap install pulsar-compose

Chocolatey (Windows):

.. code-block:: bash

   choco install pulsar-compose

Nix (Linux/macOS):

.. code-block:: bash

   nix-env -iA nixpkgs.pulsar-compose

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