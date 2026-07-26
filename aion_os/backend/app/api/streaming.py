"""SSE (Server-Sent Events) streaming endpoint.

Provides lightweight streaming for LLM responses without WebSocket.
"""

from __future__ import annotations

from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.router import AgentContext, RouterAgent
from app.core.deps import get_current_user_id, get_db
from app.llm.adapter import LLMAdapter
from app.llm.streaming import format_sse
from app.memory.manager import MemoryManager
from app.memory.store import ConversationStore

router = APIRouter(prefix="/api/v1")


@router.get("/chat/stream")
async def chat_stream_sse(
    q: str = Query(..., description="Message text"),
    conversation_id: str = Query("", description="Conversation ID"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Stream LLM response as Server-Sent Events.

    Usage:
        GET /api/v1/chat/stream?q=Привет&conversation_id=xxx

    Yields:
        event: start — metadata
        event: message — text chunks
        event: done — completion signal
        event: error — error message
    """
    from fastapi.responses import StreamingResponse

    conv_id = conversation_id or f"sse_{user_id}_{id(q)}"
    store = ConversationStore()

    # Store user message
    await store.add_message(user_id, "user", q)

    # Build context
    system_prompt = LLMAdapter.build_system_prompt({"first_name": "", "language_code": "ru"})
    memory_mgr = MemoryManager()
    memory_context = await memory_mgr.format_for_context(user_id)
    if memory_context:
        system_prompt += f"\n\n{memory_context}"

    messages = await store.format_as_messages(user_id, system_prompt, limit=10)

    async def event_generator() -> AsyncGenerator[str, None]:
        yield format_sse({
            "conversation_id": conv_id,
            "status": "started",
        }, event="start")

        router_agent = RouterAgent()
        full_response = ""

        try:
            async for chunk in router_agent.chat_stream(messages):
                full_response += chunk
                yield format_sse({"text": chunk}, event="message")

            # Store response
            await store.add_message(user_id, "assistant", full_response)

            yield format_sse({
                "text": full_response,
                "conversation_id": conv_id,
                "status": "complete",
            }, event="done")

        except Exception as e:
            yield format_sse({
                "message": str(e),
                "conversation_id": conv_id,
            }, event="error")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
