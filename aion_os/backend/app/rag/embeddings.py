"""Embeddings service — generate vector embeddings for RAG."""

from __future__ import annotations

from openai import AsyncOpenAI

from app.config import settings


class EmbeddingsService:
    """Generate embeddings for text chunks.

    Uses a dedicated embeddings model (BAAI/bge-m3 by default).
    Falls back to OpenAI-compatible endpoint if local model is unavailable.
    """

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key="not-needed",
            base_url=settings.EMBEDDINGS_API_BASE,
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors (each is a list of floats).
        """
        if not texts:
            return []

        try:
            response = await self._client.embeddings.create(
                model=settings.EMBEDDINGS_MODEL,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception:
            # Fallback: use OpenAI-compatible embedding API
            return await self._fallback_embed(texts)

    async def _fallback_embed(self, texts: list[str]) -> list[list[float]]:
        """Fallback to OpenAI or DeepSeek embedding API."""
        from openai import AsyncOpenAI

        # Try OpenAI API key fallback
        api_key = settings.OPENAI_API_KEY or settings.DEEPSEEK_API_KEY
        if api_key:
            client = AsyncOpenAI(api_key=api_key)
            try:
                response = await client.embeddings.create(
                    model="text-embedding-3-small",
                    input=texts,
                )
                return [item.embedding for item in response.data]
            except Exception:
                pass

        # Last resort: return zero vectors (RAG will degrade gracefully)
        import numpy as np
        dim = settings.EMBEDDINGS_DIMENSIONS
        return [np.zeros(dim).tolist() for _ in texts]
