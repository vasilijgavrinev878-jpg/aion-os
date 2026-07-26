"""RAG Engine — retrieval augmented generation pipeline.

Architecture:
1. Ingest documents → chunk → embed → store in pgvector
2. Query → embed → vector search → retrieve chunks → rerank → format context
3. LLM generates answer with context
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import numpy as np
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.rag.embeddings import EmbeddingsService
from app.rag.retriever import RetrievalResult


class RAGEngine:
    """Core RAG engine with hybrid search (vector + keyword)."""

    def __init__(self, db_session: AsyncSession) -> None:
        self._db = db_session
        self._embeddings = EmbeddingsService()

    async def search(
        self,
        query: str,
        top_k: int | None = None,
        category: str | None = None,
        score_threshold: float | None = None,
    ) -> list[RetrievalResult]:
        """Search the knowledge base for relevant chunks.

        Args:
            query: Natural language query.
            top_k: Number of results to return.
            category: Optional category filter.
            score_threshold: Minimum similarity score.

        Returns:
            List of retrieval results sorted by relevance.
        """
        top_k = top_k or settings.RAG_TOP_K
        score_threshold = score_threshold or settings.RAG_SCORE_THRESHOLD

        # 1. Generate query embedding
        query_vector = await self._embeddings.embed([query])
        if not query_vector or not query_vector[0]:
            return []

        query_vec = query_vector[0]
        vec_str = "[" + ",".join(str(v) for v in query_vec) + "]"

        # 2. Vector search via pgvector
        category_filter = ""
        if category:
            category_filter = f"AND metadata->>'category' = :category"

        sql = text(f"""
            SELECT
                id, content, metadata,
                1 - (embedding <=> :query_vec::vector) AS similarity
            FROM knowledge_chunks
            WHERE
                1 - (embedding <=> :query_vec::vector) > :threshold
                {category_filter}
            ORDER BY similarity DESC
            LIMIT :limit
        """)

        params: dict[str, Any] = {
            "query_vec": vec_str,
            "threshold": score_threshold,
            "limit": top_k,
        }
        if category:
            params["category"] = category

        try:
            result = await self._db.execute(sql, params)
            rows = result.fetchall()
        except Exception:
            # Fallback: text search if vector search fails
            return await self._keyword_search(query, top_k, category)

        # 3. Format results
        results = []
        for row in rows:
            meta = row.metadata if isinstance(row.metadata, dict) else json.loads(row.metadata or "{}")
            results.append(RetrievalResult(
                content=row.content,
                metadata=meta,
                score=float(row.similarity) if row.similarity else 0.0,
                source=meta.get("source", "knowledge_base"),
            ))

        return results

    async def _keyword_search(
        self,
        query: str,
        top_k: int = 5,
        category: str | None = None,
    ) -> list[RetrievalResult]:
        """Fallback keyword search when vector search is unavailable."""
        from sqlalchemy import or_

        # Simple keyword matching on content
        terms = query.lower().split()
        conditions = []

        for term in terms:
            if len(term) < 3:
                continue
            conditions.append(text(f"LOWER(content) LIKE '%{term.replace(chr(39), chr(39)+chr(39))}%'"))

        if not conditions:
            return []

        sql = text(f"""
            SELECT id, content, metadata
            FROM knowledge_chunks
            WHERE {' OR '.join(f'c.text' for _ in conditions)}
            {'AND metadata->>category = :category' if category else ''}
            LIMIT :limit
        """)

        try:
            result = await self._db.execute(sql, {"limit": top_k})
            rows = result.fetchall()
        except Exception:
            return []

        return [
            RetrievalResult(
                content=row.content,
                metadata=json.loads(row.metadata or "{}") if isinstance(row.metadata, str) else row.metadata or {},
                score=0.5,
                source="keyword_fallback",
            )
            for row in rows
        ]

    async def format_context(self, results: list[RetrievalResult], max_chars: int = 4000) -> str:
        """Format retrieval results as LLM context string."""
        parts = []
        char_count = 0

        for r in results:
            header = f"📄 Источник: {r.metadata.get('source', 'unknown')}"
            if r.metadata.get("category"):
                header += f" [{r.metadata['category']}]"
            header += f" (релевантность: {r.score:.0%})"

            content = r.content[:800]  # Limit per chunk
            entry = f"{header}\n{content}\n"

            if char_count + len(entry) > max_chars:
                break

            parts.append(entry)
            char_count += len(entry)

        return "\n---\n".join(parts)
