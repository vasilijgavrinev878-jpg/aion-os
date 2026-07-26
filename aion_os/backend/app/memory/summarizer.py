"""Conversation summarizer — creates summaries for long-term memory.

Periodically summarizes conversation history to:
- Reduce storage requirements
- Maintain context without full history
- Enable long-term memory across sessions
"""

from __future__ import annotations

from typing import Any

from app.config import settings
from app.llm.adapter import LLMAdapter


class ConversationSummarizer:
    """Summarizes conversations for compact long-term storage."""

    SUMMARIZE_PROMPT = """Суммируй диалог с пользователем в 2-3 предложения.
Выдели только важное: какие услуги интересовали, что решили, что нужно запомнить.

Диалог:
{messages}

Сводка (на русском, 2-3 предложения):
"""

    def __init__(self) -> None:
        self._llm = LLMAdapter()

    async def summarize(
        self,
        messages: list[dict[str, Any]],
    ) -> str:
        """Summarize a list of conversation messages.

        Args:
            messages: List of {role, content} dicts.

        Returns:
            Short summary string.
        """
        if not messages:
            return ""

        # Format messages for prompt
        message_text = "\n".join(
            f"{m.get('role', 'user')}: {m.get('content', '')[:200]}"
            for m in messages[-10:]
        )

        try:
            response = await self._llm.chat([
                {"role": "user", "content": self.SUMMARIZE_PROMPT.format(messages=message_text)},
            ], temperature=0.2, max_tokens=200)
            return response.content.strip()
        except Exception:
            return ""

    async def should_summarize(self, message_count: int) -> bool:
        """Check if conversation should be summarized based on length."""
        return message_count > 0 and message_count % settings.MEMORY_SUMMARY_INTERVAL == 0
