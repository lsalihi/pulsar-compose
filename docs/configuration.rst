Configuration
=============

Pulsar can be configured through environment variables, configuration files, and command-line options.

Environment Variables
---------------------

API Keys
~~~~~~~~

Set API keys for AI providers:

.. code-block:: bash

   # OpenAI
   export OPENAI_API_KEY="sk-..."

   # Anthropic
   export ANTHROPIC_API_KEY="sk-ant-..."

   # Together AI (optional)
   export TOGETHER_API_KEY="..."

   # Other providers as needed

Ollama Configuration
~~~~~~~~~~~~~~~~~~~~

Configure local Ollama instance:

.. code-block:: bash

   # Ollama server URL (default: http://localhost:11434)
   export OLLAMA_BASE_URL="http://localhost:11434"

   # Model to use (can be overridden in workflows)
   export OLLAMA_DEFAULT_MODEL="llama2"

Application Settings
~~~~~~~~~~~~~~~~~~~~

Control Pulsar behavior:

.. code-block:: bash

   # Log level (DEBUG, INFO, WARNING, ERROR)
   export PULSAR_LOG_LEVEL="INFO"

   # Default timeout for API calls (seconds)
   export PULSAR_TIMEOUT="30"

   # Maximum concurrent requests
   export PULSAR_MAX_CONCURRENT="5"

   # Cache directory for downloaded models
   export PULSAR_CACHE_DIR="~/.cache/pulsar"

Configuration File
------------------

Create a ``.pulsar.toml`` or ``pulsar.toml`` file in your project directory:

.. code-block:: toml

   [api_keys]
   openai = "sk-..."
   anthropic = "sk-ant-..."

   [ollama]
   base_url = "http://localhost:11434"
   default_model = "llama2"

   [app]
   log_level = "INFO"
   timeout = 30
   max_concurrent = 5
   cache_dir = "~/.cache/pulsar"

   [providers.openai]
   organization = "org-..."  # Optional
   api_base = "https://api.openai.com/v1"  # Optional

   [providers.anthropic]
   api_base = "https://api.anthropic.com"  # Optional

   [providers.ollama]
   timeout = 60  # Override default timeout

Workflow-Specific Configuration
-------------------------------

Override settings in individual workflows:

.. code-block:: yaml

   version: "0.1"
   name: "Configured Workflow"

   config:
     timeout: 60
     max_retries: 3
     log_level: "DEBUG"

   agents:
     # ... agent definitions

   workflow:
     # ... workflow steps

Command-Line Options
--------------------

Override configuration from command line:

.. code-block:: bash

   # Set log level
   pulsar --log-level DEBUG run workflow.yml

   # Set timeout
   pulsar --timeout 60 run workflow.yml

   # Use specific config file
   pulsar --config /path/to/config.toml run workflow.yml

   # Set API keys inline (not recommended for production)
   pulsar --openai-key sk-... run workflow.yml

Available CLI options:

.. code-block:: text

   --log-level LEVEL       Set logging level
   --timeout SECONDS       API call timeout
   --max-concurrent N      Maximum concurrent requests
   --config FILE          Configuration file path
   --openai-key KEY       OpenAI API key
   --anthropic-key KEY    Anthropic API key
   --ollama-url URL       Ollama base URL

Provider-Specific Settings
--------------------------

OpenAI
~~~~~~

.. code-block:: toml

   [providers.openai]
   api_key = "sk-..."
   organization = "org-..."
   api_base = "https://api.openai.com/v1"
   timeout = 30
   max_retries = 3

Anthropic
~~~~~~~~~

.. code-block:: toml

   [providers.anthropic]
   api_key = "sk-ant-..."
   api_base = "https://api.anthropic.com"
   timeout = 30
   max_retries = 3
   max_tokens = 4096

Ollama
~~~~~~

.. code-block:: toml

   [providers.ollama]
   base_url = "http://localhost:11434"
   timeout = 60
   default_model = "llama2"
   request_timeout = 300  # For long-running generations

Proxy Configuration
-------------------

Configure HTTP proxies for API calls:

.. code-block:: bash

   export HTTP_PROXY="http://proxy.company.com:8080"
   export HTTPS_PROXY="http://proxy.company.com:8080"
   export NO_PROXY="localhost,127.0.0.1,.local"

Or in configuration file:

.. code-block:: toml

   [proxy]
   http = "http://proxy.company.com:8080"
   https = "http://proxy.company.com:8080"
   no_proxy = "localhost,127.0.0.1,.local"

Security Considerations
-----------------------

**API Keys**

- Never commit API keys to version control
- Use environment variables or secure key management
- Rotate keys regularly
- Use read-only keys when possible

**Network Security**

- Use HTTPS for all API communications
- Configure proxies for corporate environments
- Validate SSL certificates

**File Permissions**

- Restrict access to configuration files
- Use secure file permissions (600) for sensitive files

**Environment Isolation**

- Use virtual environments for Python dependencies
- Isolate different projects with separate configurations
- Use Docker containers for consistent environments

Configuration Validation
------------------------

Pulsar validates configuration on startup:

.. code-block:: bash

   # Validate configuration
   pulsar config validate

   # Show current configuration
   pulsar config show

   # Check provider connectivity
   pulsar config test-providers

Example Configurations
----------------------

**Development Environment**

.. code-block:: toml

   [app]
   log_level = "DEBUG"
   timeout = 60

   [api_keys]
   openai = "sk-test-..."

   [providers.openai]
   api_base = "https://api.openai.com/v1"

**Production Environment**

.. code-block:: toml

   [app]
   log_level = "WARNING"
   timeout = 30
   max_concurrent = 10

   [api_keys]
   openai = "sk-prod-..."
   anthropic = "sk-ant-prod-..."

   [providers.openai]
   organization = "org-prod"
   timeout = 30

   [providers.anthropic]
   timeout = 30

**Local Development with Ollama**

.. code-block:: toml

   [app]
   log_level = "INFO"

   [ollama]
   base_url = "http://localhost:11434"
   default_model = "llama2"

   [providers.ollama]
   timeout = 120