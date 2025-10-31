import asyncio
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from anthropic import AsyncAnthropic
from .base import BaseAgent, AgentResult, AgentConfig

class AnthropicAgent(BaseAgent):
    """Anthropic agent implementation supporting Claude models."""

    def __init__(self, config: AgentConfig):
        if not config.api_key:
            raise ValueError("Anthropic API key is required")
        self.client = AsyncAnthropic(api_key=config.api_key)
        self.config = config

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((Exception, asyncio.TimeoutError))
    )
    async def execute(self, prompt: str, model: str, **parameters) -> AgentResult:
        """Execute Anthropic API call with retry logic."""
        try:
            # Extract system prompt if provided
            system = parameters.pop("system", None)
            
            # Build messages
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            # Merge default parameters
            params = {
                "model": model,
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0.7,
                **parameters
            }

            response = await asyncio.wait_for(
                self.client.messages.create(**params),
                timeout=self.config.timeout
            )

            output = response.content[0].text if response.content else ""

            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }

            cost = self.estimate_cost(usage, model)

            return AgentResult(
                output=output,
                usage=usage,
                model=model,
                metadata={
                    "stop_reason": response.stop_reason,
                    "provider": "anthropic"
                },
                cost=cost
            )

        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")

    def estimate_cost(self, usage: Dict[str, int], model: str) -> float:
        """Estimate cost in USD based on token usage."""
        # Pricing as of 2024 (approximate, should be updated)
        pricing = {
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},  # per 1K tokens
            "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
            "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125}
        }

        if model not in pricing:
            return 0.0

        rates = pricing[model]
        input_cost = (usage.get("input_tokens", 0) / 1000) * rates["input"]
        output_cost = (usage.get("output_tokens", 0) / 1000) * rates["output"]

        return round(input_cost + output_cost, 6)