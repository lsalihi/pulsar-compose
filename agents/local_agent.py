import asyncio
import aiohttp
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .base import BaseAgent, AgentResult, AgentConfig

class LocalAgent(BaseAgent):
    """Local agent implementation for Ollama and similar local models."""

    def __init__(self, config: AgentConfig):
        self.base_url = config.base_url or "http://localhost:11434"
        self.config = config
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def execute(self, prompt: str, model: str, **parameters) -> AgentResult:
        """Execute local model API call with retry logic."""
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            # Ollama API format
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                **parameters
            }

            url = f"{self.base_url}/api/generate"

            async with self.session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Ollama API error {response.status}: {error_text}")

                data = await response.json()

                output = data.get("response", "")

                # Map Ollama usage to standard format
                usage = {
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                }

                cost = self.estimate_cost(usage, model)  # Always 0 for local

                return AgentResult(
                    output=output,
                    usage=usage,
                    model=model,
                    metadata={
                        "done": data.get("done", False),
                        "provider": "local",
                        "context_length": len(data.get("context", []))
                    },
                    cost=cost
                )

        except aiohttp.ClientError as e:
            raise RuntimeError(f"Local API connection error: {e}")
        except asyncio.TimeoutError:
            raise RuntimeError("Local API request timed out")
        except RuntimeError:
            # Re-raise RuntimeError (like API errors) as-is
            raise
        except Exception as e:
            raise RuntimeError(f"Unexpected error in local agent: {e}")

    def estimate_cost(self, usage: Dict[str, int], model: str) -> float:
        """Local models have no cost."""
        return 0.0