"""Memory Manager — orchestrates long-term user memory across sessions.

Architecture:
1. Extract key facts from conversation
2. Store in PostgreSQL with timestamps and relevance scores
3. Retrieve on subsequent interactions
4. Decay old memories automatically
5. Allow user CRUD on their memories
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.llm.adapter import LLMAdapter


class MemoryManager:
    """Manages long-term user memory with extraction, storage, and retrieval."""

    EXTRACT_MEMORY_PROMPT = """Извлеки важную информацию о пользователе из диалога.

Диалог пользователя: {message}

Извлеки ТОЛЬКО факты, которые стоит запомнить:
- Имя, язык, город
- Любимые категории услуг
- Предпочтения по услугам
- Важные события/даты
- Контактные данные

Ответь ТОЛЬКО в формате JSON:
{{
    "facts": [
        {{"key": "preferred_city", "value": "Нячанг", "type": "preference"}},
        {{"key": "loves_category", "value": "медицина", "type": "category"}}
    ]
}}

Если нечего запоминать — верни {{"facts": []}}
"""

    def __init__(self, db_session: AsyncSession | None = None) -> None:
        self._db = db_session
        self._llm = LLMAdapter()

    async def extract_and_store(
        self,
        user_id: int,
        message: str,
        response: str,
    ) -> list[dict[str, Any]]:
        """Extract facts from conversation and store in memory."""
        # 1. Extract facts using LLM
        facts = await self._extract_facts(message)

        # 2. Store each fact
        stored = []
        for fact in facts:
            try:
                await self._store_fact(user_id, fact)
                stored.append(fact)
            except Exception:
                continue

        return stored

    async def retrieve(self, user_id: int, limit: int = 20) -> list[dict[str, Any]]:
        """Retrieve user's stored memories."""
        from app.db.session import async_session_factory
        from app.models.memory import UserMemory

        async with async_session_factory() as session:
            result = await session.execute(
                select(UserMemory)
                .where(UserMemory.user_id == user_id)
                .order_by(UserMemory.relevance.desc(), UserMemory.updated_at.desc())
                .limit(limit)
            )
            memories = result.scalars().all()

            return [
                {
                    "key": m.memory_key,
                    "value": m.memory_value,
                    "type": m.memory_type,
                    "relevance": m.relevance,
                    "updated": m.updated_at.isoformat() if m.updated_at else "",
                }
                for m in memories
            ]

    async def format_for_context(self, user_id: int) -> str:
        """Format user memories as context string for LLM."""
        memories = await self.retrieve(user_id)
        if not memories:
            return ""

        parts = [f"📝 Информация о пользователе (из долговременной памяти):"]
        for m in memories[:15]:
            parts.append(f"• {m['key']}: {m['value']}")

        return "\n".join(parts)

    async def delete_all(self, user_id: int) -> int:
        """Delete all memories for a user."""
        from app.db.session import async_session_factory
        from app.models.memory import UserMemory

        async with async_session_factory() as session:
            result = await session.execute(
                delete(UserMemory).where(UserMemory.user_id == user_id)
            )
            await session.commit()
            return result.rowcount

    async def delete_key(self, user_id: int, key: str) -> bool:
        """Delete a specific memory key for a user."""
        from app.db.session import async_session_factory
        from app.models.memory import UserMemory

        async with async_session_factory() as session:
            result = await session.execute(
                delete(UserMemory).where(
                    UserMemory.user_id == user_id,
                    UserMemory.memory_key == key,
                )
            )
            await session.commit()
            return result.rowcount > 0

    async def update_relevance(self, user_id: int, key: str) -> None:
        """Boost relevance when a memory is used."""
        from app.db.session import async_session_factory
        from app.models.memory import UserMemory

        async with async_session_factory() as session:
            await session.execute(
                update(UserMemory)
                .where(
                    UserMemory.user_id == user_id,
                    UserMemory.memory_key == key,
                )
                .values(relevance=1.0, updated_at=datetime.now(timezone.utc))
            )
            await session.commit()

    async def _extract_facts(self, message: str) -> list[dict[str, str]]:
        """Extract facts from a user message."""
        prompt = self.EXTRACT_MEMORY_PROMPT.format(message=message[:500])
        try:
            response = await self._llm.chat([
                {"role": "user", "content": prompt},
            ], temperature=0.1, max_tokens=300)

            text = response.content.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            data = json.loads(text)
            return data.get("facts", [])
        except Exception:
            return []

    async def _store_fact(self, user_id: int, fact: dict[str, str]) -> None:
        """Store a single fact in database."""
        from app.db.session import async_session_factory
        from app.models.memory import UserMemory

        key = fact.get("key", "")
        value = fact.get("value", "")
        fact_type = fact.get("type", "preference")

        if not key or not value:
            return

        async with async_session_factory() as session:
            # Check if exists
            existing = await session.execute(
                select(UserMemory).where(
                    UserMemory.user_id == user_id,
                    UserMemory.memory_key == key,
                )
            )
            existing_mem = existing.scalar_one_or_none()

            if existing_mem:
                # Update
                existing_mem.memory_value = value
                existing_mem.relevance = 1.0
                existing_mem.updated_at = datetime.now(timezone.utc)
            else:
                # Create
                mem = UserMemory(
                    user_id=user_id,
                    memory_type=fact_type,
                    memory_key=key,
                    memory_value=value,
                    relevance=1.0,
                )
                session.add(mem)

            await session.commit()
