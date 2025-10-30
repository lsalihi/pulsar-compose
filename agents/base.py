from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any, Dict, Optional
from dataclasses import dataclass

class AgentResult(BaseModel):
    """Result from agent execution."""
    output: Any
    usage: Dict[str, int] = {}
    model: str
    metadata: Dict[str, Any] = {}
    cost: Optional[float] = None  # Estimated cost in USD

class BaseAgent(ABC):
    """Abstract base class for all AI agent providers."""

    @abstractmethod
    async def execute(self, prompt: str, model: str, **parameters) -> AgentResult:
        """Execute the agent with given prompt and parameters."""
        pass

    @abstractmethod
    def estimate_cost(self, usage: Dict[str, int], model: str) -> float:
        """Estimate cost based on token usage."""
        pass

@dataclass
class AgentConfig:
    """Configuration for agent providers."""
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60
    max_retries: int = 3