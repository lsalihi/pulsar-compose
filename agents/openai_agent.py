import asyncio
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import AsyncOpenAI, OpenAIError
from .base import BaseAgent, AgentResult, AgentConfig

class OpenAIAgent(BaseAgent):
    """OpenAI agent implementation supporting GPT models."""

    def __init__(self, config: AgentConfig):
        if not config.api_key:
            raise ValueError("OpenAI API key is required")
        self.client = AsyncOpenAI(api_key=config.api_key)
        self.config = config

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OpenAIError, asyncio.TimeoutError))
    )
    async def execute(self, prompt: str, model: str, **parameters) -> AgentResult:
        """Execute OpenAI API call with retry logic."""
        try:
            # Merge default parameters
            params = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                **parameters
            }

            response = await asyncio.wait_for(
                self.client.chat.completions.create(**params),
                timeout=self.config.timeout
            )

            choice = response.choices[0]
            output = choice.message.content

            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

            cost = self.estimate_cost(usage, model)

            return AgentResult(
                output=output,
                usage=usage,
                model=model,
                metadata={
                    "finish_reason": choice.finish_reason,
                    "provider": "openai"
                },
                cost=cost
            )

        except OpenAIError as e:
            raise RuntimeError(f"OpenAI API error: {e}")
        except asyncio.TimeoutError:
            raise RuntimeError("OpenAI API request timed out")
        except Exception as e:
            raise RuntimeError(f"Unexpected error in OpenAI agent: {e}")

    def estimate_cost(self, usage: Dict[str, int], model: str) -> float:
        """Estimate cost in USD based on token usage."""
        # Pricing as of 2024 (approximate, should be updated)
        pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
        }

        if model not in pricing:
            return 0.0

        rates = pricing[model]
        input_cost = (usage.get("prompt_tokens", 0) / 1000) * rates["input"]
        output_cost = (usage.get("completion_tokens", 0) / 1000) * rates["output"]

        return round(input_cost + output_cost, 6)