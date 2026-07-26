"""DeepSeek LLM provider — primary provider via DeepSeek API."""

from __future__ import annotations

from typing import Any, AsyncGenerator

from openai import AsyncOpenAI

from app.config import settings
from app.llm.adapter import BaseLLMProvider, LLMResponse


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek API provider — high-quality, low-cost, strong Russian support."""

    provider_name = "deepseek"

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY or settings.OPENAI_API_KEY,
            base_url=settings.DEEPSEEK_API_BASE,
        )

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:
        response = await self._client.chat.completions.create(
            model=model or settings.LLM_DEFAULT_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools if tools else None,
        )
        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            tool_calls=[t.model_dump() for t in (choice.message.tool_calls or [])],
            model=response.model,
            usage=response.usage.model_dump() if response.usage else {},
            finish_reason=choice.finish_reason or "",
        )

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncGenerator[str, None]:
        stream = await self._client.chat.completions.create(
            model=model or settings.LLM_DEFAULT_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools if tools else None,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content

    async def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        """DeepSeek doesn't have native embeddings — use OpenAI or local."""
        from app.rag.embeddings import EmbeddingsService
        svc = EmbeddingsService()
        return await svc.embed(texts)
