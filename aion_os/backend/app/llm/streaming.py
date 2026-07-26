"""Streaming utilities — SSE formatting, token counting, etc."""

from __future__ import annotations

import json
from typing import AsyncGenerator


def format_sse(data: dict | str, event: str = "message") -> str:
    """Format data as Server-Sent Event."""
    if isinstance(data, dict):
        payload = json.dumps(data, ensure_ascii=False)
    else:
        payload = str(data)
    return f"event: {event}\ndata: {payload}\n\n"


async def sse_wrap(
    content_stream: AsyncGenerator[str, None],
    metadata: dict | None = None,
) -> AsyncGenerator[str, None]:
    """Wrap an async content generator as SSE events.

    Yields:
        event: start — metadata
        event: message — content chunks
        event: done — final metadata
    """
    if metadata:
        yield format_sse(metadata, event="start")

    async for chunk in content_stream:
        if chunk:
            yield format_sse({"text": chunk}, event="message")

    yield format_sse({"status": "complete"}, event="done")


def count_tokens(text: str, model: str = "deepseek-chat") -> int:
    """Approximate token count using tiktoken if available."""
    try:
        import tiktoken
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except ImportError:
        # Fallback: ~1.5 chars per token for Russian
        return int(len(text) / 1.5)
