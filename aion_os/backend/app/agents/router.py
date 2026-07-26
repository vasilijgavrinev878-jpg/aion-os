"""Router Agent — the entry point for all user messages.

Architecture (three-tier routing):

    User Message
         │
         ▼
    ┌─────────────────────┐
    │ 1. COMMAND ROUTER   │  ◄── Fast path (μs), no LLM
    │  (regex patterns)   │      Navigation, greetings, help
    └─────────┬───────────┘
         │                    matched → AgentResult (instant)
         │ unmatched
         ▼
    ┌─────────────────────┐
    │ 2. INTENT CACHE     │  ◄── LRU cache (ms), no LLM call
    │  (recent intents)   │      Repeated/similar queries
    └─────────┬───────────┘
         │                    cache hit → intent from cache
         │ cache miss
         ▼
    ┌─────────────────────┐
    │ 3. LLM CLASSIFY     │  ◄── LLM call (1-3s)
    │  (intent + route)   │      → store result in cache
    └─────────┬───────────┘
         │
         ▼
    Specialist Agent (Search, Booking, CRM, etc.)

Benefits:
- Navigation commands: 0 LLM calls (was 2: classify + navigate)
- Repeated queries: 0 LLM calls (cached after first)
- Greetings/help: 0 LLM calls (static responses)
- Complex queries: 1 LLM call (same as before)
"""

from __future__ import annotations

import json
import time
from typing import Any

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.search import SearchAgent
from app.agents.knowledge import KnowledgeAgent
from app.agents.booking import BookingAgent
from app.agents.crm import CRMAgent
from app.agents.navigation import NavigationAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.partner import PartnerAgent
from app.agents.command_router import CommandRouter
from app.agents.intent_cache import IntentCache
from app.config import settings
from app.llm.adapter import LLMAdapter


# Shared class-level cache across all RouterAgent instances
_intent_cache = IntentCache(max_size=200, ttl_seconds=300)
_command_router = CommandRouter()


class RouterAgent(BaseAgent):
    """Routes user messages to the correct specialist agent.

    Three-tier routing:
    1. CommandRouter — instant pattern matching (no LLM)
    2. IntentCache — recent/similar intent classifications (no LLM)
    3. LLM — full intent classification for complex queries
    """

    agent_name = "router"
    agent_description = "Classifies intent and routes to the correct agent"

    # Intent classification prompt (only used as fallback)
    CLASSIFICATION_PROMPT = """Определи намерение пользователя на русском языке.

Категории намерений:
- search: Поиск услуг, товаров, партнёров. "Найди стоматолога", "Где снять квартиру", "Ищу врача"
- booking: Бронирование, заказ, запись. "Запиши на массаж", "Хочу заказать уборку", "Забронируй"
- navigate: Навигация по приложению. "Открой раздел недвижимость", "Покажи категории", "Открой мой профиль"
- knowledge: Вопросы по проекту, документации, FAQ. "Что такое AION", "Какие есть категории"
- partner: Поиск/информация о партнёрах. "Найди партнёра по клинингу", "Покажи всех врачей"
- crm: Заявки, заказы, история. "Мои заказы", "Статус брони", "Отмени заказ"
- memory: Запоминание/напоминание. "Запомни что я люблю", "Напомни", "Мои предпочтения"
- chat: Общий разговор, приветствие, помощь. "Привет", "Что ты умеешь", "Помоги"

Сообщение: {message}

Ответь ТОЛЬКО в формате JSON:
{{"intent": "search|booking|navigate|knowledge|partner|crm|memory|chat", "confidence": 0.0-1.0, "entities": {{"category": "", "location": "", "keywords": []}} }}
"""

    def __init__(self) -> None:
        super().__init__()
        self._agents: dict[str, BaseAgent] | None = None

    def _get_agents(self) -> dict[str, BaseAgent]:
        if self._agents is None:
            self._agents = {
                "search": SearchAgent(),
                "knowledge": KnowledgeAgent(),
                "booking": BookingAgent(),
                "crm": CRMAgent(),
                "navigate": NavigationAgent(),
                "memory": MemoryAgent(),
                "partner": PartnerAgent(),
            }
        return self._agents

    async def execute(self, ctx: AgentContext) -> AgentResult:
        """Execute routing: CommandRouter → IntentCache → LLM → Specialist Agent."""
        start = time.monotonic()

        # ─── TIER 1: Command Router (instant, no LLM) ───────────
        result = _command_router.route(ctx.message)
        if result is not None:
            result.latency_ms = (time.monotonic() - start) * 1000
            self.log_agent_action(
                ctx, f"command_router:{result.navigation.get('action', 'static') if result.navigation else 'static'}",
                latency_ms=result.latency_ms,
            )
            return result

        # ─── TIER 2: Intent Cache (no LLM, ~0.1ms) ─────────────
        cache_key = _intent_cache.make_key(ctx.message)
        cached = _intent_cache.get(cache_key)
        if cached is not None:
            # Fuzzy match — also check similar messages
            intent = cached
        else:
            # Try fuzzy match for similar messages
            intent = _intent_cache.get_fuzzy(ctx.message, threshold=0.7)

        if intent is not None:
            # Route using cached intent
            result = await self._route_by_intent(ctx, intent, start)
            self.log_agent_action(
                ctx, f"cache_hit:{intent.get('intent', '?')}",
                latency_ms=result.latency_ms,
            )
            return result

        # ─── TIER 3: LLM Intent Classification ─────────────────
        intent = await self._classify_intent(ctx.message)

        # Store in cache for future hits
        _intent_cache.store_with_text(ctx.message, intent)

        # Route using classified intent
        result = await self._route_by_intent(ctx, intent, start)
        self.log_agent_action(
            ctx, f"llm_classified:{intent.get('intent', '?')}",
            latency_ms=result.latency_ms,
        )
        return result

    async def _route_by_intent(
        self,
        ctx: AgentContext,
        intent: dict[str, Any],
        start: float,
    ) -> AgentResult:
        """Route to the appropriate specialist agent based on intent classification."""
        agent_map = self._get_agents()
        intent_name = intent.get("intent", "chat")
        agent = agent_map.get(intent_name)

        if agent is None:
            # Default: use LLM directly
            response = await self._llm.chat([
                {"role": "system", "content": self._build_system_prompt(ctx)},
                {"role": "user", "content": ctx.message},
            ])
            latency = (time.monotonic() - start) * 1000
            return AgentResult(response=response.content, latency_ms=latency)

        # Execute specialist agent
        try:
            ctx.metadata["intent"] = intent
            result = await agent.execute(ctx)
            result.latency_ms = (time.monotonic() - start) * 1000
            return result
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            self.log_agent_action(
                ctx, f"{agent.agent_name}_error", status="error",
                error_message=str(e), latency_ms=latency,
            )
            # Fallback: direct LLM
            response = await self._llm.chat([
                {"role": "system", "content": self._build_system_prompt(ctx)},
                {"role": "user", "content": ctx.message},
            ])
            return AgentResult(response=response.content, latency_ms=latency)

    async def _classify_intent(self, message: str) -> dict[str, Any]:
        """Classify the user's intent using the LLM.

        Only called when CommandRouter and IntentCache both miss.
        """
        prompt = self.CLASSIFICATION_PROMPT.format(message=message[:500])
        try:
            response = await self._llm.chat([
                {"role": "user", "content": prompt},
            ], temperature=0.1, max_tokens=200)

            # Parse JSON response
            text = response.content.strip()
            # Handle markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            intent = json.loads(text)
            return intent
        except (json.JSONDecodeError, Exception):
            return {"intent": "chat", "confidence": 0.5, "entities": {}}

    def _build_system_prompt(self, ctx: AgentContext) -> str:
        return LLMAdapter.build_system_prompt({
            "first_name": ctx.user_name,
            "language_code": ctx.user_lang,
        })

    @staticmethod
    def clear_cache() -> None:
        """Clear the shared intent cache (useful for testing)."""
        _intent_cache.clear()

    @staticmethod
    def cache_stats() -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": _intent_cache.size,
            "max_size": 200,
            "ttl_seconds": 300,
            "supported_commands": CommandRouter.pattern_count(),
        }
