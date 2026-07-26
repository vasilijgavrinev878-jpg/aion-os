"""Retrieval types and document chunking utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RetrievalResult:
    """A single retrieved chunk from the knowledge base."""

    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    source: str = "knowledge_base"

    def __repr__(self) -> str:
        return f"<RetrievalResult {self.source} ({self.score:.0%})>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content[:200],
            "metadata": self.metadata,
            "score": self.score,
            "source": self.source,
        }


# ─── Document Chunking ─────────────────────────────────────


def chunk_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> list[str]:
    """Split text into overlapping chunks.

    Uses semantic boundaries (paragraphs, sentences) when possible.
    Falls back to fixed-size chunking with overlap.

    Args:
        text: Input text to chunk.
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between chunks in characters.

    Returns:
        List of text chunks.
    """
    if not text:
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # Try to find a good break point (paragraph, sentence)
        if end < text_len:
            # Look for paragraph break
            para_break = text.rfind("\n\n", start + chunk_size // 2, end)
            if para_break > start:
                end = para_break + 2
            else:
                # Look for sentence end
                for sep in [". ", "! ", "? ", ".\n", ".\r"]:
                    sent_end = text.rfind(sep, start + chunk_size // 2, end)
                    if sent_end > start:
                        end = sent_end + 2
                        break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - chunk_overlap
        if start >= text_len:
            break

    return chunks


def chunk_document(
    title: str,
    content: str,
    source: str,
    metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Chunk a full document into indexed pieces.

    Returns:
        List of dicts with keys: content, metadata (title, source, etc.)
    """
    meta = {"title": title, "source": source, **(metadata or {})}
    chunks = chunk_text(content, settings_chunk_size(), settings_chunk_overlap())

    return [
        {"content": chunk, "metadata": {**meta, "chunk_index": i}}
        for i, chunk in enumerate(chunks)
    ]


def settings_chunk_size() -> int:
    """Get chunk size from settings."""
    from app.config import settings
    return settings.RAG_CHUNK_SIZE


def settings_chunk_overlap() -> int:
    """Get chunk overlap from settings."""
    from app.config import settings
    return settings.RAG_CHUNK_OVERLAP
