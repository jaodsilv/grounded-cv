"""Base Agent class for GroundedCV AI agents."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

from anthropic import AsyncAnthropic

from app.config import settings


@dataclass
class AgentMetadata:
    """Metadata about an agent execution."""

    agent_name: str
    model_used: str
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0
    cost_usd: float = 0.0
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None

    def calculate_cost(self) -> float:
        """Calculate the cost based on model and tokens used."""
        pricing = {
            "claude-opus-4-5-20251101": {"input": 0.015, "output": 0.075},
            "claude-sonnet-4-5-20250929": {"input": 0.003, "output": 0.015},
            "claude-3-5-haiku-20241022": {"input": 0.001, "output": 0.005},
        }
        if self.model_used in pricing:
            rates = pricing[self.model_used]
            self.cost_usd = (self.tokens_in / 1000) * rates["input"] + (
                self.tokens_out / 1000
            ) * rates["output"]
        return self.cost_usd


@dataclass
class AgentResponse:
    """Response from an agent execution."""

    status: Literal["success", "error", "partial"]
    output: Any
    metadata: AgentMetadata
    errors: list[str] = field(default_factory=list)


class BaseAgent(ABC):
    """Base class for all AI agents in GroundedCV."""

    def __init__(self, name: str, model: str | None = None):
        """Initialize the agent.

        Args:
            name: Unique name for this agent
            model: Model to use (defaults to balanced model)
        """
        self.name = name
        self.model = model or settings.model_balanced
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.logger = logging.getLogger(f"grounded-cv.agents.{name}")

    @abstractmethod
    async def run(self, *args, **kwargs) -> AgentResponse:
        """Execute the agent's main task.

        Must be implemented by subclasses.
        """
        pass

    async def _call_claude(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> tuple[str, AgentMetadata]:
        """Call Claude API and return response with metadata.

        Args:
            prompt: The user prompt to send
            system: Optional system prompt
            model: Model to use (defaults to agent's model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Tuple of (response_text, metadata)
        """
        model = model or self.model
        max_tokens = max_tokens or settings.max_tokens

        metadata = AgentMetadata(
            agent_name=self.name,
            model_used=model,
        )

        messages = [{"role": "user", "content": prompt}]
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
        }

        if system:
            kwargs["system"] = system

        if temperature != 0.7:
            kwargs["temperature"] = temperature

        self.logger.debug(f"Calling {model} with {len(prompt)} chars")

        response = await self.client.messages.create(**kwargs)

        metadata.completed_at = datetime.now()
        metadata.latency_ms = int(
            (metadata.completed_at - metadata.started_at).total_seconds() * 1000
        )
        metadata.tokens_in = response.usage.input_tokens
        metadata.tokens_out = response.usage.output_tokens
        metadata.calculate_cost()

        self.logger.debug(
            f"Response: {metadata.tokens_out} tokens, "
            f"${metadata.cost_usd:.4f}, {metadata.latency_ms}ms"
        )

        return response.content[0].text, metadata

    async def _stream_claude(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ):
        """Stream Claude API response.

        Args:
            prompt: The user prompt to send
            system: Optional system prompt
            model: Model to use (defaults to agent's model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Yields:
            Text chunks as they arrive
        """
        model = model or self.model
        max_tokens = max_tokens or settings.max_tokens

        messages = [{"role": "user", "content": prompt}]
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
        }

        if system:
            kwargs["system"] = system

        if temperature != 0.7:
            kwargs["temperature"] = temperature

        self.logger.debug(f"Streaming from {model}")

        async with self.client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text

            message = await stream.get_final_message()
            self.logger.debug(f"Stream complete: {message.usage.output_tokens} tokens")
