"""Knowledge base ingestion — chunk, embed, and store documents."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.rag.embeddings import EmbeddingsService
from app.rag.retriever import chunk_document


class IngestionService:
    """Ingest documents into the knowledge base.

    Supports:
    - Text files
    - JSON data
    - HTML documents (stripped)
    - CSV data
    """

    def __init__(self, db_session: AsyncSession) -> None:
        self._db = db_session
        self._embeddings = EmbeddingsService()

    async def ingest_file(self, filepath: str, source: str | None = None) -> int:
        """Ingest a single file into the knowledge base.

        Args:
            filepath: Path to the file.
            source: Source identifier (default: filename).

        Returns:
            Number of chunks ingested.
        """
        path = Path(filepath)
        source = source or path.stem

        if not path.exists():
            return 0

        content = path.read_text(encoding="utf-8", errors="ignore")

        if path.suffix == ".html":
            import re
            content = re.sub(r"<[^>]+>", " ", content)
            content = re.sub(r"\s+", " ", content).strip()

        chunks = chunk_document(
            title=path.stem,
            content=content,
            source=source,
            metadata={"file": path.name, "type": path.suffix},
        )

        return await self._store_chunks(chunks)

    async def ingest_text(
        self,
        title: str,
        content: str,
        source: str,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Ingest a text string into the knowledge base."""
        chunks = chunk_document(title, content, source, metadata)
        return await self._store_chunks(chunks)

    async def ingest_json(self, json_path: str) -> int:
        """Ingest structured JSON data."""
        path = Path(json_path)
        if not path.exists():
            return 0

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        total = 0
        if isinstance(data, list):
            for item in data:
                title = item.get("name", item.get("title", "untitled"))
                content = json.dumps(item, ensure_ascii=False)
                total += await self.ingest_text(title, content, path.stem)
        elif isinstance(data, dict):
            for key, value in data.items():
                total += await self.ingest_text(key, str(value), path.stem)

        return total

    async def ingest_directory(self, directory: str) -> dict[str, int]:
        """Ingest all supported files from a directory."""
        path = Path(directory)
        if not path.is_dir():
            return {}

        results = {}
        for file_path in path.rglob("*"):
            if file_path.suffix in {".txt", ".html", ".json", ".csv", ".md"}:
                count = await self.ingest_file(str(file_path))
                if count > 0:
                    results[file_path.name] = count

        return results

    async def _store_chunks(self, chunks: list[dict[str, Any]]) -> int:
        """Store chunks in pgvector database."""
        if not chunks:
            return 0

        texts = [c["content"] for c in chunks]
        embeddings = await self._embeddings.embed(texts)

        stored = 0
        for chunk, embedding in zip(chunks, embeddings):
            if embedding is None or all(v == 0.0 for v in embedding):
                continue

            chunk_id = hashlib.md5(chunk["content"].encode()).hexdigest()
            vec_str = "[" + ",".join(str(v) for v in embedding) + "]"

            sql = text("""
                INSERT INTO knowledge_chunks (id, content, metadata, embedding)
                VALUES (:id, :content, :metadata, :embedding::vector)
                ON CONFLICT (id) DO UPDATE SET
                    content = EXCLUDED.content,
                    metadata = EXCLUDED.metadata,
                    embedding = EXCLUDED.embedding
            """)

            try:
                await self._db.execute(sql, {
                    "id": chunk_id,
                    "content": chunk["content"],
                    "metadata": json.dumps(chunk["metadata"], ensure_ascii=False),
                    "embedding": vec_str,
                })
                stored += 1
            except Exception:
                continue

        await self._db.commit()
        return stored
