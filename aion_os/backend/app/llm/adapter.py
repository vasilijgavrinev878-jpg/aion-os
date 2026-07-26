"""Universal LLM Adapter — provider-agnostic model interface.

Design:
- Single interface for all LLM providers
- Switch providers via config without changing application code
- Supports streaming, async, tool calling
- Built-in fallback if primary provider is down
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Protocol

from app.config import settings


# ─── Unified types ────────────────────────────────────────


class LLMMessage(Protocol):
    role: str  # system, user, assistant
    content: str


class LLMToolCall(Protocol):
    name: str
    arguments: dict[str, Any]


class LLMResponse:
    """Unified response from any LLM provider."""

    def __init__(
        self,
        content: str = "",
        tool_calls: list[dict[str, Any]] | None = None,
        model: str = "",
        usage: dict[str, int] | None = None,
        finish_reason: str = "",
        latency_ms: float = 0.0,
    ) -> None:
        self.content = content
        self.tool_calls = tool_calls or []
        self.model = model
        self.usage = usage or {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        self.finish_reason = finish_reason
        self.latency_ms = latency_ms

    def __repr__(self) -> str:
        return f"<LLMResponse {self.model} ({self.usage['total_tokens']}t) {self.finish_reason}>"


# ─── Base Provider ────────────────────────────────────────


class BaseLLMProvider(ABC):
    """Abstract base for all LLM providers."""

    provider_name: str = "base"

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:
        """Non-streaming chat completion."""
        ...

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Streaming chat completion — yields content chunks."""
        ...  # pragma: no cover
        yield ""

    @abstractmethod
    async def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        ...


# ─── LLM Adapter ──────────────────────────────────────────


class LLMAdapter:
    """Unified LLM adapter — routes to the correct provider.

    Usage:
        llm = LLMAdapter()
        response = await llm.chat([{"role": "user", "content": "Hello"}])
        async for chunk in llm.chat_stream([{"role": "user", "content": "Hello"}]):
            print(chunk)
    """

    def __init__(self, provider_name: str | None = None) -> None:
        self._provider_name = provider_name or settings.LLM_DEFAULT_PROVIDER
        self._provider: BaseLLMProvider | None = None

    async def _get_provider(self) -> BaseLLMProvider:
        """Lazy-load the appropriate provider based on config."""
        if self._provider is not None:
            return self._provider

        provider_name = self._provider_name or settings.LLM_DEFAULT_PROVIDER

        if provider_name == "deepseek":
            from app.llm.providers.deepseek import DeepSeekProvider
            self._provider = DeepSeekProvider()
        elif provider_name == "qwen":
            from app.llm.providers.qwen import QwenProvider
            self._provider = QwenProvider()
        elif provider_name == "llama":
            from app.llm.providers.llama import LlamaProvider
            self._provider = LlamaProvider()
        elif provider_name == "openai":
            from app.llm.providers.openai_provider import OpenAIProvider
            self._provider = OpenAIProvider()
        else:
            # Default to DeepSeek
            from app.llm.providers.deepseek import DeepSeekProvider
            self._provider = DeepSeekProvider()

        return self._provider

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:
        """Send a chat completion request to the configured provider."""
        provider = await self._get_provider()
        start = time.monotonic()
        try:
            response = await provider.chat(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools,
            )
            response.latency_ms = (time.monotonic() - start) * 1000
            return response
        except Exception as e:
            # Fallback to backup provider
            fallback = await self._get_fallback_provider(provider.provider_name)
            if fallback:
                start = time.monotonic()
                response = await fallback.chat(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=tools,
                )
                response.latency_ms = (time.monotonic() - start) * 1000
                return response
            raise

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream a chat completion response."""
        provider = await self._get_provider()
        async for chunk in provider.chat_stream(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
        ):
            yield chunk

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using the provider's embedding model."""
        provider = await self._get_provider()
        return await provider.embed(texts)

    async def _get_fallback_provider(self, failed_provider: str) -> BaseLLMProvider | None:
        """Try to get a fallback provider if the primary one fails."""
        fallbacks = {
            "deepseek": "openai",
            "qwen": "deepseek",
            "llama": "qwen",
            "openai": "deepseek",
        }
        fb_name = fallbacks.get(failed_provider)
        if fb_name and fb_name != failed_provider:
            self._provider_name = fb_name
            self._provider = None
            return await self._get_provider()
        return None

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @staticmethod
    def build_system_prompt(user_info: dict[str, Any] | None = None) -> str:
        """Build the base system prompt for AION assistant."""
        name = (user_info or {}).get("first_name", "пользователь")
        lang = (user_info or {}).get("language_code", "ru")

        return f"""Ты — AION, AI-ассистент операционной системы для жизни людей за границей.

ОСНОВНЫЕ ПРАВИЛА:
1. Отвечай на {'русском' if lang == 'ru' else 'английском'} языке.
2. Ты помогаешь пользователю найти услуги, партнёров, оформить заказы.
3. У AION есть 23 категории услуг: недвижимость, визы, транспорт, медицина, страхование, еда, клининг, красота, дети, животные, экскурсии, спорт, психология, фото, цветы, мероприятия, образование, прокат, экстренная помощь, ремонт, страховка, обмен валюты, шопинг.
4. Если пользователь просит найти что-то — используй инструменты поиска.
5. Если нужно создать бронь или заказ — используй инструменты CRM.
6. Будь дружелюбным, но по делу. Имя пользователя: {name}.
7. Если не знаешь точного ответа — скажи честно, но предложи смежные варианты.
8. Всегда уточняй детали: город, бюджет, предпочтения."""
