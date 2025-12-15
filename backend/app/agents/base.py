"""Base Agent class for GroundedCV AI agents using Claude Agent SDK."""

import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    query,
)

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
    session_id: str | None = None

    @classmethod
    def from_result_message(
        cls,
        agent_name: str,
        model: str,
        result: ResultMessage,
        started_at: datetime,
    ) -> "AgentMetadata":
        """Create metadata from SDK ResultMessage.

        Args:
            agent_name: Name of the agent
            model: Model used for the request
            result: ResultMessage from claude-agent-sdk
            started_at: When the request started

        Returns:
            AgentMetadata instance populated from the result
        """
        usage = result.usage or {}
        return cls(
            agent_name=agent_name,
            model_used=model,
            tokens_in=usage.get("input_tokens", 0),
            tokens_out=usage.get("output_tokens", 0),
            latency_ms=result.duration_ms,
            cost_usd=result.total_cost_usd or 0.0,
            started_at=started_at,
            completed_at=datetime.now(),
            session_id=result.session_id,
        )

    def calculate_cost(self) -> float:
        """Calculate the cost based on model and tokens used.

        This is a fallback method when SDK doesn't provide cost.
        Uses current Claude pricing (December 2024).

        Returns:
            Calculated cost in USD
        """
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
    """Base class for all AI agents in GroundedCV.

    Supports two modes of operation:
    1. Stateless mode (query): Each call creates a new session
    2. Conversational mode (ClaudeSDKClient): Maintains session state

    Built-in tools are enabled by default, allowing agents to autonomously
    read/write files, run commands, search the web, etc.

    Example usage - Stateless:
        class MyAgent(BaseAgent):
            async def run(self, task: str) -> AgentResponse:
                text, metadata = await self._call_claude(task)
                return AgentResponse(status="success", output=text, metadata=metadata)

    Example usage - Conversational:
        async with MyAgent("agent") as agent:
            response1, _ = await agent._continue_conversation("First question")
            response2, meta = await agent._continue_conversation("Follow-up")
    """

    # Default built-in tools available to all agents
    DEFAULT_TOOLS = [
        "Read",
        "Write",
        "Edit",
        "Bash",
        "Glob",
        "Grep",
        "WebSearch",
        "WebFetch",
    ]

    def __init__(
        self,
        name: str,
        model: str | None = None,
        tools: list[str] | None = None,
        system_prompt: str | None = None,
    ):
        """Initialize the agent.

        Args:
            name: Unique name for this agent
            model: Model to use (defaults to balanced model from settings)
            tools: List of allowed tools (defaults to DEFAULT_TOOLS)
            system_prompt: Optional system prompt for this agent
        """
        self.name = name
        self.model = model or settings.model_balanced
        self.tools = tools if tools is not None else self.DEFAULT_TOOLS
        self.system_prompt = system_prompt
        self.logger = logging.getLogger(f"grounded-cv.agents.{name}")

        # Client for conversational mode (lazy initialization)
        self._client: ClaudeSDKClient | None = None

    def _get_options(
        self,
        system_prompt: str | None = None,
        tools: list[str] | None = None,
        max_turns: int | None = None,
    ) -> ClaudeAgentOptions:
        """Build ClaudeAgentOptions with common settings.

        Args:
            system_prompt: Override system prompt for this call
            tools: Override tools for this call
            max_turns: Maximum conversation turns

        Returns:
            ClaudeAgentOptions configured for this agent
        """
        return ClaudeAgentOptions(
            model=self.model,
            system_prompt=system_prompt or self.system_prompt,
            allowed_tools=tools if tools is not None else self.tools,
            max_turns=max_turns or settings.max_iterations,
            permission_mode="acceptEdits",  # Auto-accept for automation
            cwd=str(settings.data_dir.resolve()),
        )

    @abstractmethod
    async def run(self, *args: Any, **kwargs: Any) -> AgentResponse:
        """Execute the agent's main task.

        Must be implemented by subclasses.

        Returns:
            AgentResponse with status, output, and metadata
        """
        pass

    # --- Stateless API (query) ---

    async def _call_claude(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        tools: list[str] | None = None,
        max_turns: int | None = None,
    ) -> tuple[str, AgentMetadata]:
        """Call Claude API (stateless) and return response with metadata.

        Uses the query() function - creates a new session for each call.
        Best for one-off tasks that don't need conversation history.

        Args:
            prompt: The user prompt to send
            system: Optional system prompt (overrides agent default)
            model: Model to use (overrides agent default)
            tools: Tools to enable (overrides agent default)
            max_turns: Maximum conversation turns

        Returns:
            Tuple of (response_text, metadata)
        """
        used_model = model or self.model
        started_at = datetime.now()

        options = ClaudeAgentOptions(
            model=used_model,
            system_prompt=system or self.system_prompt,
            allowed_tools=tools if tools is not None else self.tools,
            max_turns=max_turns or settings.max_iterations,
            permission_mode="acceptEdits",
            cwd=str(settings.data_dir.resolve()),
        )

        self.logger.debug(f"Calling {used_model} with {len(prompt)} chars (stateless)")

        response_text = ""
        metadata: AgentMetadata | None = None

        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_text += block.text
            elif isinstance(message, ResultMessage):
                metadata = AgentMetadata.from_result_message(
                    agent_name=self.name,
                    model=used_model,
                    result=message,
                    started_at=started_at,
                )

        if metadata is None:
            # Fallback if no ResultMessage received
            metadata = AgentMetadata(
                agent_name=self.name,
                model_used=used_model,
                started_at=started_at,
                completed_at=datetime.now(),
            )

        self.logger.debug(
            f"Response: {metadata.tokens_out} tokens, "
            f"${metadata.cost_usd:.4f}, {metadata.latency_ms}ms"
        )

        return response_text, metadata

    async def _stream_claude(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        tools: list[str] | None = None,
        max_turns: int | None = None,
    ) -> AsyncIterator[str]:
        """Stream Claude API response (stateless).

        Uses the query() function - creates a new session for each call.
        Yields text chunks as they arrive.

        Args:
            prompt: The user prompt to send
            system: Optional system prompt
            model: Model to use
            tools: Tools to enable
            max_turns: Maximum conversation turns

        Yields:
            Text chunks as they arrive
        """
        used_model = model or self.model

        options = ClaudeAgentOptions(
            model=used_model,
            system_prompt=system or self.system_prompt,
            allowed_tools=tools if tools is not None else self.tools,
            max_turns=max_turns or settings.max_iterations,
            permission_mode="acceptEdits",
            cwd=str(settings.data_dir.resolve()),
        )

        self.logger.debug(f"Streaming from {used_model} (stateless)")

        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        yield block.text

        self.logger.debug("Stream complete")

    # --- Conversational API (ClaudeSDKClient) ---

    async def _start_conversation(
        self,
        initial_prompt: str | None = None,
        system: str | None = None,
        tools: list[str] | None = None,
    ) -> None:
        """Start a new conversation session.

        Uses ClaudeSDKClient for maintaining conversation state.
        Best for multi-turn interactions where context matters.

        Args:
            initial_prompt: Optional first message to send
            system: Optional system prompt
            tools: Tools to enable
        """
        options = self._get_options(system_prompt=system, tools=tools)
        self._client = ClaudeSDKClient(options=options)
        await self._client.connect(prompt=initial_prompt)
        self.logger.debug("Started conversation session")

    async def _continue_conversation(
        self,
        prompt: str,
    ) -> tuple[str, AgentMetadata | None]:
        """Continue an existing conversation.

        Args:
            prompt: The message to send

        Returns:
            Tuple of (response_text, metadata or None)

        Raises:
            RuntimeError: If no conversation session is active
        """
        if self._client is None:
            raise RuntimeError("No active conversation. Call _start_conversation() first.")

        started_at = datetime.now()
        await self._client.query(prompt)

        response_text = ""
        metadata: AgentMetadata | None = None

        async for message in self._client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_text += block.text
            elif isinstance(message, ResultMessage):
                metadata = AgentMetadata.from_result_message(
                    agent_name=self.name,
                    model=self.model,
                    result=message,
                    started_at=started_at,
                )

        return response_text, metadata

    async def _stream_conversation(
        self,
        prompt: str,
    ) -> AsyncIterator[str]:
        """Stream response in an ongoing conversation.

        Args:
            prompt: The message to send

        Yields:
            Text chunks as they arrive

        Raises:
            RuntimeError: If no conversation session is active
        """
        if self._client is None:
            raise RuntimeError("No active conversation. Call _start_conversation() first.")

        await self._client.query(prompt)

        async for message in self._client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        yield block.text

    async def _end_conversation(self) -> None:
        """End the current conversation session."""
        if self._client is not None:
            await self._client.disconnect()
            self._client = None
            self.logger.debug("Ended conversation session")

    async def __aenter__(self) -> "BaseAgent":
        """Async context manager entry - starts conversation."""
        await self._start_conversation()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Async context manager exit - ends conversation."""
        await self._end_conversation()


async def quick_query(
    prompt: str,
    system_prompt: str | None = None,
    model: str | None = None,
    tools: list[str] | None = None,
) -> str:
    """Quick one-off query without creating an agent instance.

    Convenience function for simple queries that don't need
    agent tracking or metadata.

    Args:
        prompt: The prompt to send
        system_prompt: Optional system prompt
        model: Model to use (defaults to balanced)
        tools: Tools to enable (defaults to all built-in)

    Returns:
        Response text from Claude
    """
    options = ClaudeAgentOptions(
        model=model or settings.model_balanced,
        system_prompt=system_prompt,
        allowed_tools=tools or BaseAgent.DEFAULT_TOOLS,
        permission_mode="acceptEdits",
        cwd=str(settings.data_dir.resolve()),
    )

    response_text = ""
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    response_text += block.text

    return response_text
