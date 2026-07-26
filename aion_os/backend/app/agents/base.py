"""Base agent — all AI agents inherit from this."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.llm.adapter import LLMAdapter, LLMResponse


@dataclass
class AgentContext:
    """Context passed to every agent execution."""

    user_id: int
    user_name: str = ""
    user_lang: str = "ru"
    message: str = ""
    session: AsyncSession | None = None
    conversation_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from an agent execution."""

    success: bool = True
    response: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    navigation: dict[str, Any] | None = None  # {action: "open_category", params: {...}}
    cards: list[dict[str, Any]] | None = None  # Service cards to display
    error_message: str = ""
    latency_ms: float = 0.0
    should_escalate: bool = False


class BaseAgent(ABC):
    """Base class for all AION agents."""

    agent_name: str = "base"
    agent_description: str = ""
    required_tools: list[str] = field(default_factory=list)  # noqa: F811

    def __init__(self) -> None:
        self._llm = LLMAdapter()

    @abstractmethod
    async def execute(self, ctx: AgentContext) -> AgentResult:
        """Execute the agent's primary function."""
        ...

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
    ) -> LLMResponse:
        """Send a chat request with system prompt."""
        return await self._llm.chat(
            messages=messages,
            temperature=temperature,
        )

    async def chat_stream(self, messages: list[dict[str, str]]):
        """Stream a chat response."""
        async for chunk in self._llm.chat_stream(messages=messages):
            yield chunk

    def log_agent_action(
        self,
        ctx: AgentContext,
        action: str,
        status: str = "success",
        input_data: str = "",
        output_data: str = "",
        latency_ms: float = 0.0,
        error_message: str = "",
    ) -> None:
        """Log agent action to database for monitoring."""
        # This would be async in production
        import logging
        logger = logging.getLogger(f"agent.{self.agent_name}")
        logger.info(
            f"[{status}] {action} | user={ctx.user_id} | "
            f"latency={latency_ms:.0f}ms | {error_message if error_message else ''}"
        )
