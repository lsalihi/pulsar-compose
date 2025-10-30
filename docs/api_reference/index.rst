API Reference
=============

This section provides comprehensive documentation for Pulsar's Python API.

Core Classes
============

Pulsar Engine
-------------

.. automodule:: engine.executor
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: engine.expression_evaluator
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: engine.results
   :members:
   :undoc-members:
   :show-inheritance:

Agent System
============

Base Agent
----------

.. automodule:: agents.base
   :members:
   :undoc-members:
   :show-inheritance:

Agent Factory
-------------

.. automodule:: agents.factory
   :members:
   :undoc-members:
   :show-inheritance:

Provider Agents
---------------

OpenAI Agent
~~~~~~~~~~~~

.. automodule:: agents.openai_agent
   :members:
   :undoc-members:
   :show-inheritance:

Anthropic Agent
~~~~~~~~~~~~~~~

.. automodule:: agents.anthropic_agent
   :members:
   :undoc-members:
   :show-inheritance:

Local Agent (Ollama)
~~~~~~~~~~~~~~~~~~~~

.. automodule:: agents.local_agent
   :members:
   :undoc-members:
   :show-inheritance:

Agent Configuration
-------------------

.. automodule:: agents.config
   :members:
   :undoc-members:
   :show-inheritance:

CLI Interface
=============

Main CLI
--------

.. automodule:: cli.main
   :members:
   :undoc-members:
   :show-inheritance:

CLI Configuration
-----------------

.. automodule:: cli.config
   :members:
   :undoc-members:
   :show-inheritance:

History Management
------------------

.. automodule:: cli.history
   :members:
   :undoc-members:
   :show-inheritance:

Progress Tracking
-----------------

.. automodule:: cli.progress
   :members:
   :undoc-members:
   :show-inheritance:

Plugin System
-------------

.. automodule:: cli.plugins
   :members:
   :undoc-members:
   :show-inheritance:

Input Providers
===============

Base Provider
-------------

.. automodule:: input_providers.base
   :members:
   :undoc-members:
   :show-inheritance:

Console Provider
~~~~~~~~~~~~~~~~

.. automodule:: input_providers.console
   :members:
   :undoc-members:
   :show-inheritance:

File Provider
~~~~~~~~~~~~~

.. automodule:: input_providers.file
   :members:
   :undoc-members:
   :show-inheritance:

Web Provider
~~~~~~~~~~~~

.. automodule:: input_providers.web
   :members:
   :undoc-members:
   :show-inheritance:

Test Provider
~~~~~~~~~~~~~

.. automodule:: input_providers.test
   :members:
   :undoc-members:
   :show-inheritance:

Step Handlers
=============

Base Handler
------------

.. automodule:: step_handlers.base
   :members:
   :undoc-members:
   :show-inheritance:

Agent Handler
~~~~~~~~~~~~~

.. automodule:: step_handlers.agent_handler
   :members:
   :undoc-members:
   :show-inheritance:

Condition Handler
~~~~~~~~~~~~~~~~~

.. automodule:: step_handlers.condition_handler
   :members:
   :undoc-members:
   :show-inheritance:

Interaction Handler
~~~~~~~~~~~~~~~~~~~

.. automodule:: step_handlers.interaction_handler
   :members:
   :undoc-members:
   :show-inheritance:

Models
======

.. automodule:: models
   :members:
   :undoc-members:
   :show-inheritance:

State Management
~~~~~~~~~~~~~~~~

.. automodule:: models.state
   :members:
   :undoc-members:
   :show-inheritance:

Template System
~~~~~~~~~~~~~~~

.. automodule:: models.template
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
==========

.. automodule:: engine.executor
   :members:
   :exclude-members: WorkflowExecutor

.. automodule:: agents.base
   :members:
   :exclude-members: BaseAgent

.. automodule:: cli.main
   :members:
   :exclude-members: main

Utility Functions
=================

Expression Evaluation
---------------------

.. automodule:: engine.expression_evaluator
   :members:
   :exclude-members: ExpressionEvaluator

Configuration Helpers
---------------------

.. automodule:: cli.config
   :members:
   :exclude-members: CLIConfig

Plugin Loading
--------------

.. automodule:: cli.plugins
   :members:
   :exclude-members: PluginManager

Type Definitions
================

.. code-block:: python

   from typing import Dict, List, Optional, Union, Any
   from pathlib import Path

   # Workflow types
   WorkflowConfig = Dict[str, Any]
   StepConfig = Dict[str, Any]
   AgentConfig = Dict[str, Any]

   # Execution types
   ExecutionResult = Dict[str, Any]
   StepResult = Dict[str, Any]

   # Provider types
   InputData = Union[str, Dict[str, Any], List[Any]]

   # Template types
   TemplateVars = Dict[str, Any]
   RenderedTemplate = str

Constants
=========

.. code-block:: python

   # Version information
   __version__ = "0.1.0"

   # Supported providers
   SUPPORTED_PROVIDERS = ["openai", "anthropic", "ollama"]

   # Default timeouts (seconds)
   DEFAULT_AGENT_TIMEOUT = 30
   DEFAULT_STEP_TIMEOUT = 60

   # Retry configuration
   DEFAULT_MAX_RETRIES = 3
   DEFAULT_BACKOFF_FACTOR = 2.0

   # Model defaults
   DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"
   DEFAULT_ANTHROPIC_MODEL = "claude-3-haiku-20240307"
   DEFAULT_OLLAMA_MODEL = "llama2"

   # File extensions
   WORKFLOW_EXTENSIONS = [".yml", ".yaml"]
   CONFIG_EXTENSIONS = [".toml", ".json", ".yaml", ".yml"]

Environment Variables
=====================

Core Configuration
------------------

.. envvar:: PULSAR_CONFIG_FILE

   Path to configuration file. Default: ``~/.pulsar/config.toml``

.. envvar:: PULSAR_WORKFLOW_DIR

   Directory containing workflow files. Default: ``./workflows``

.. envvar:: PULSAR_LOG_LEVEL

   Logging level (DEBUG, INFO, WARNING, ERROR). Default: ``INFO``

.. envvar:: PULSAR_LOG_FILE

   Path to log file. Default: ``~/.pulsar/pulsar.log``

Provider Configuration
----------------------

OpenAI
~~~~~~

.. envvar:: OPENAI_API_KEY

   OpenAI API key (required for OpenAI agents)

.. envvar:: OPENAI_BASE_URL

   OpenAI API base URL. Default: ``https://api.openai.com/v1``

.. envvar:: OPENAI_TIMEOUT

   OpenAI API timeout in seconds. Default: ``30``

Anthropic
~~~~~~~~~

.. envvar:: ANTHROPIC_API_KEY

   Anthropic API key (required for Anthropic agents)

.. envvar:: ANTHROPIC_BASE_URL

   Anthropic API base URL. Default: ``https://api.anthropic.com``

.. envvar:: ANTHROPIC_TIMEOUT

   Anthropic API timeout in seconds. Default: ``30``

Ollama
~~~~~~

.. envvar:: OLLAMA_BASE_URL

   Ollama API base URL. Default: ``http://localhost:11434``

.. envvar:: OLLAMA_TIMEOUT

   Ollama API timeout in seconds. Default: ``60``

Execution Configuration
-----------------------

.. envvar:: PULSAR_MAX_CONCURRENT_STEPS

   Maximum concurrent step execution. Default: ``5``

.. envvar:: PULSAR_DEFAULT_TIMEOUT

   Default step timeout in seconds. Default: ``300``

.. envvar:: PULSAR_MAX_RETRIES

   Default maximum retries for failed steps. Default: ``3``

.. envvar:: PULSAR_BACKOFF_FACTOR

   Retry backoff factor. Default: ``2.0``

CLI Configuration
-----------------

.. envvar:: PULSAR_HISTORY_SIZE

   Maximum command history size. Default: ``1000``

.. envvar:: PULSAR_PROGRESS_STYLE

   Progress bar style (auto, plain, rich). Default: ``auto``

.. envvar:: PULSAR_COLORS

   Enable/disable colored output. Default: ``true``