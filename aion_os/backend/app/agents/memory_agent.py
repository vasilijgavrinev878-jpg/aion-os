"""Memory Agent — manages user preferences and long-term memory.

Responsibility:
- Store user preferences and facts
- Recall stored information
- Update/delete memory
- Summarize conversation history
"""

from __future__ import annotations

import json
import time

from app.agents.base import AgentContext, AgentResult, BaseAgent


class MemoryAgent(BaseAgent):
    """Manages user preferences, facts, and long-term memory."""

    agent_name = "memory"
    agent_description = "Stores and retrieves user preferences"

    MEMORY_PROMPT = """Определи, что нужно сделать с памятью пользователя.

Сообщение: {message}

Варианты:
- remember: Пользователь хочет, чтобы что-то запомнили. "Запомни что я люблю ...", "Мой любимый ресторан ..."
- recall: Пользователь спрашивает что мы о нём знаем. "Что ты обо мне знаешь?", "Какие мои предпочтения?"
- forget: Пользователь хочет удалить информацию. "Забудь ...", "Удали мои данные"
- update: Пользователь меняет предпочтения. "Теперь я люблю другое ..."

Ответь ТОЛЬКО в формате JSON:
{{"action": "remember|recall|forget|update", "key": "ключ памяти", "value": "значение", "type": "preference|fact|category"}}
"""

    async def execute(self, ctx: AgentContext) -> AgentResult:
        start = time.monotonic()

        # 1. Classify memory action
        memory_action = await self._classify_action(ctx.message)
        action = memory_action.get("action", "recall")
        key = memory_action.get("key", "")
        value = memory_action.get("value", "")

        if action == "remember" and key and value:
            # Store in database
            if ctx.session and key and value:
                from app.db.session import async_session_factory
                from app.models.memory import UserMemory

                async with async_session_factory() as session:
                    mem = UserMemory(
                        user_id=ctx.user_id,
                        memory_type=memory_action.get("type", "preference"),
                        memory_key=key,
                        memory_value=value,
                    )
                    session.add(mem)
                    await session.commit()

            response = f"✅ Запомнил! {key}: {value}"
            latency = (time.monotonic() - start) * 1000
            self.log_agent_action(ctx, f"memory_remember:{key}", latency_ms=latency)
            return AgentResult(response=response, latency_ms=latency)

        elif action == "recall":
            # Recall stored memories
            memories = []
            if ctx.session:
                from app.db.session import async_session_factory
                from app.models.memory import UserMemory
                from sqlalchemy import select

                async with async_session_factory() as session:
                    result = await session.execute(
                        select(UserMemory).where(UserMemory.user_id == ctx.user_id)
                    )
                    memories = result.scalars().all()

            if not memories:
                response = "Пока ничего о вас не знаю. Расскажите о своих предпочтениях!"
            else:
                memory_list = "\n".join(
                    f"• {m.memory_key}: {m.memory_value}" for m in memories[-10:]
                )
                response = f"📝 Что я знаю о вас:\n{memory_list}"

            latency = (time.monotonic() - start) * 1000
            return AgentResult(response=response, data={"memories": [str(m) for m in memories]}, latency_ms=latency)

        elif action in ("forget", "update"):
            if ctx.session and key:
                from app.db.session import async_session_factory
                from app.models.memory import UserMemory
                from sqlalchemy import delete

                async with async_session_factory() as session:
                    await session.execute(
                        delete(UserMemory).where(
                            UserMemory.user_id == ctx.user_id,
                            UserMemory.memory_key == key,
                        )
                    )
                    await session.commit()

            response = f"✅ Выполнено. Больше не буду хранить: {key}" if action == "forget" else f"✅ Обновил: {key} -> {value}"
            return AgentResult(response=response)

        return AgentResult(
            response="Я могу запоминать ваши предпочтения. Просто скажите: 'Запомни что я люблю...'"
        )

    async def _classify_action(self, message: str) -> dict:
        """Classify the memory action from the message."""
        prompt = self.MEMORY_PROMPT.format(message=message[:300])
        try:
            response = await self._llm.chat([
                {"role": "user", "content": prompt},
            ], temperature=0.1, max_tokens=200)
            text = response.content.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception:
            return {"action": "recall", "key": "", "value": "", "type": "preference"}
