import os
from typing import Dict, Optional
from pydantic import BaseModel, Field

class ProviderConfig(BaseModel):
    """Configuration for a specific provider."""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60
    max_retries: int = 3

class PulsarConfig(BaseModel):
    """Main configuration for Pulsar agents."""
    openai: ProviderConfig = Field(default_factory=ProviderConfig)
    anthropic: ProviderConfig = Field(default_factory=ProviderConfig)
    local: ProviderConfig = Field(default_factory=lambda: ProviderConfig(base_url="http://localhost:11434"))

    @classmethod
    def from_env(cls) -> "PulsarConfig":
        """Load configuration from environment variables."""
        return cls(
            openai=ProviderConfig(
                api_key=os.getenv("OPENAI_API_KEY"),
                timeout=int(os.getenv("OPENAI_TIMEOUT", "60")),
                max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "3"))
            ),
            anthropic=ProviderConfig(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                timeout=int(os.getenv("ANTHROPIC_TIMEOUT", "60")),
                max_retries=int(os.getenv("ANTHROPIC_MAX_RETRIES", "3"))
            ),
            local=ProviderConfig(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                timeout=int(os.getenv("OLLAMA_TIMEOUT", "60")),
                max_retries=int(os.getenv("OLLAMA_MAX_RETRIES", "3"))
            )
        )

    @classmethod
    def from_dict(cls, config_dict: Dict) -> "PulsarConfig":
        """Load configuration from dictionary."""
        return cls(**config_dict)