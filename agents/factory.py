from typing import Dict, Any, Optional
from .base import BaseAgent, AgentConfig
from .openai_agent import OpenAIAgent
from .anthropic_agent import AnthropicAgent
from .local_agent import LocalAgent
from .config import PulsarConfig

class AgentFactory:
    """Factory for creating agent instances based on provider."""

    def __init__(self, config: PulsarConfig):
        self.config = config
        self._agents: Dict[str, BaseAgent] = {}

    def get_agent(self, provider: str, agent_name: Optional[str] = None) -> BaseAgent:
        """Get or create an agent instance for the given provider."""
        if provider not in self._agents:
            self._agents[provider] = self._create_agent(provider)
        return self._agents[provider]

    def _create_agent(self, provider: str) -> BaseAgent:
        """Create a new agent instance."""
        if provider == "openai":
            config = AgentConfig(
                provider=provider,
                api_key=self.config.openai.api_key,
                timeout=self.config.openai.timeout,
                max_retries=self.config.openai.max_retries
            )
            return OpenAIAgent(config)
        elif provider == "anthropic":
            config = AgentConfig(
                provider=provider,
                api_key=self.config.anthropic.api_key,
                timeout=self.config.anthropic.timeout,
                max_retries=self.config.anthropic.max_retries
            )
            return AnthropicAgent(config)
        elif provider == "local":
            config = AgentConfig(
                provider=provider,
                base_url=self.config.local.base_url,
                timeout=self.config.local.timeout,
                max_retries=self.config.local.max_retries
            )
            return LocalAgent(config)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def list_supported_providers(self) -> list[str]:
        """List all supported providers."""
        return ["openai", "anthropic", "local"]

    async def execute_with_agent(self, provider: str, prompt: str, model: str, **parameters) -> Any:
        """Convenience method to execute with a specific provider."""
        agent = self.get_agent(provider)
        result = await agent.execute(prompt, model, **parameters)
        return result