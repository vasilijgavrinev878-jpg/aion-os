"""Navigation Agent — controls Telegram Mini App UI via commands.

Responsibility:
- Parse user intent into navigation commands
- Open categories, screens, cards, user profile
- Show search results, booking details, etc.
"""

from __future__ import annotations

import json
import time

from app.agents.base import AgentContext, AgentResult, BaseAgent

AION_NAVIGATION_ACTIONS = {
    "open_main": {"action": "open_main", "description": "Главный экран"},
    "open_categories": {"action": "open_categories", "description": "Все категории услуг"},
    "open_category": {"action": "open_category", "params": {"category": ""}, "description": "Открыть категорию"},
    "open_search": {"action": "open_search", "params": {"query": ""}, "description": "Поиск"},
    "open_profile": {"action": "open_profile", "description": "Профиль пользователя"},
    "open_bookings": {"action": "open_bookings", "description": "Мои бронирования"},
    "open_orders": {"action": "open_orders", "description": "Мои заказы"},
    "open_favorites": {"action": "open_favorites", "description": "Избранное"},
    "open_partner": {"action": "open_partner", "params": {"id": 0}, "description": "Карточка партнёра"},
    "show_cards": {"action": "show_cards", "params": {"cards": []}, "description": "Показать карточки"},
    "open_chat": {"action": "open_chat", "params": {"partner_id": 0}, "description": "Чат с партнёром"},
    "open_payment": {"action": "open_payment", "params": {"booking_id": 0}, "description": "Оплата"},
    "open_history": {"action": "open_history", "description": "История"},
    "open_map": {"action": "open_map", "params": {"lat": 0, "lng": 0}, "description": "Карта"},
    "go_back": {"action": "go_back", "description": "Назад"},
}


class NavigationAgent(BaseAgent):
    """Controls the Telegram Mini App UI through navigation commands."""

    agent_name = "navigation"
    agent_description = "Opens screens, categories, and cards in the Mini App"

    NAVIGATION_PROMPT = """Определи, какой экран нужно открыть в приложении AION.

Сообщение пользователя: {message}

Доступные действия:
- open_main — Главный экран
- open_categories — Список всех категорий
- open_category — Открыть категорию (укажи название)
- open_search — Поиск (укажи запрос)
- open_profile — Профиль пользователя
- open_bookings — Мои бронирования
- open_orders — Мои заказы
- open_favorites — Избранное
- show_cards — Показать карточки услуг
- go_back — Назад

Ответь ТОЛЬКО в формате JSON:
{{"action": "open_category|show_cards|open_search|...", "params": {{}}, "reason": "почему"}}
"""

    async def execute(self, ctx: AgentContext) -> AgentResult:
        start = time.monotonic()

        # 1. Determine navigation action
        nav_action = await self._classify_navigation(ctx.message)

        # 2. Generate response
        action_name = nav_action.get("action", "open_main")
        params = nav_action.get("params", {})

        action_config = AION_NAVIGATION_ACTIONS.get(action_name, AION_NAVIGATION_ACTIONS["open_main"])
        reason = nav_action.get("reason", "Выполняю навигацию")

        response = await self._llm.chat([
            {"role": "system", "content": f"Ты — навигационный ассистент AION. {reason}"},
            {"role": "user", "content": ctx.message},
        ])

        latency = (time.monotonic() - start) * 1000
        self.log_agent_action(ctx, f"navigate:{action_name}", latency_ms=latency)

        return AgentResult(
            response=response.content,
            navigation={"action": action_name, "params": params},
            latency_ms=latency,
        )

    async def _classify_navigation(self, message: str) -> dict:
        """Classify which navigation action to take."""
        prompt = self.NAVIGATION_PROMPT.format(message=message[:300])
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
            return {"action": "open_main", "params": {}, "reason": "стандартный ответ"}
