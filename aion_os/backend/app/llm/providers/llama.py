"""Llama LLM provider — runs via Ollama (local)."""

from __future__ import annotations

from typing import Any, AsyncGenerator

from openai import AsyncOpenAI

from app.config import settings
from app.llm.adapter import BaseLLMProvider, LLMResponse


class LlamaProvider(BaseLLMProvider):
    """Llama 3.1 — runs locally via Ollama.

    Excellent for on-premise deployment.
    Llama 3.1 70B needs dual GPU. Use 8B for single GPU.
    """

    provider_name = "llama"

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key="ollama",
            base_url=settings.LLAMA_API_BASE,
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
            model=model or settings.LLAMA_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )
        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            tool_calls=[],
            model=response.model,
            usage={},
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
            model=model or settings.LLAMA_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        from app.rag.embeddings import EmbeddingsService
        svc = EmbeddingsService()
        return await svc.embed(texts)
