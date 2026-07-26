"""Command Router — fast, no-LLM command recognition layer.

Design:
- Uses regex + keyword matching for instant response (no LLM call)
- Handles all simple commands: navigation, filter, pagination, help
- Returns AgentResult directly with navigation actions
- Measured in microseconds, not seconds

Architecture placement:
    User → CommandRouter → (matched) → AgentResult (no LLM)
                         → (unmatched) → IntentCache → LLM → RouterAgent
"""

from __future__ import annotations

import re
import time
from typing import Any

from app.agents.base import AgentResult

# ─── Navigation command patterns ──────────────────────────

NAVIGATION_PATTERNS: list[dict[str, Any]] = [
    # ── Main screens ──
    {
        "patterns": [
            r"^(открой|открыть|покажи|показать|перейди|перейти)\s+(главную|главный\s*экран|меню|главное\s*меню|домой)$",
            r"^(на\s+)?главную$",
            r"^(вернуться|вернись)\s+(на\s+)?главную",
        ],
        "intent": "navigate",
        "action": "open_main",
        "response": "Открываю главный экран",
    },
    # ── Categories ──
    {
        "patterns": [
            r"^(открой|открыть|покажи|показать)\s+(категории|категори(?:ю|и)|все\s*категории|список\s*услуг|услуги)$",
            r"^(какие|что|все)\s+(есть\s+)?категории",
            r"^(что|какие)\s+вы\s+предлагаете",
        ],
        "intent": "navigate",
        "action": "open_categories",
        "response": "Открываю список категорий",
    },
    # ── Back ──
    {
        "patterns": [
            r"^(назад|вернись|вернуться|назад\s*пожалуйста)$",
            r"^go\s*back$",
        ],
        "intent": "navigate",
        "action": "go_back",
        "response": "Возвращаюсь назад",
    },
    # ── Profile ──
    {
        "patterns": [
            r"^(открой|открыть|покажи|показать|мой)\s*(профиль|аккаунт|личный\s*кабинет)$",
            r"^(кто\s+я|мой\s+профиль|мои\s+данные|мой\s+аккаунт)$",
        ],
        "intent": "navigate",
        "action": "open_profile",
        "response": "Открываю ваш профиль",
    },
    # ── Bookings ──
    {
        "patterns": [
            r"^(открой|открыть|покажи|показать|мои)\s*(бронь|бронирования|брони|записи|заказы|заказ)$",
            r"^(где\s+)?мои\s+(бронь|бронирования|заказы|записи)$",
        ],
        "intent": "navigate",
        "action": "open_bookings",
        "response": "Открываю список ваших бронирований",
    },
    # ── Favorites ──
    {
        "patterns": [
            r"^(открой|открыть|покажи|показать|мои|мое)\s*(избранное|избранные|сохраненн(?:ое|ые)|закладки)$",
            r"^(где\s+)?мо[её]\s+избранное$",
        ],
        "intent": "navigate",
        "action": "open_favorites",
        "response": "Открываю избранное",
    },
    # ── Search ──
    {
        "patterns": [
            r"^(открой|открыть|покажи|показать)\s+поиск$",
            r"^(искать|найти|поиск)\s*$",
        ],
        "intent": "navigate",
        "action": "open_search",
        "response": "Открываю поиск",
    },
    # ── Filter commands ──
    {
        "patterns": [
            r"^(отфильтруй|отфильтровать|фильтр|измени\s+фильтр|сбрось\s+фильтр|убери\s+фильтр)$",
            r"^покажи\s+только\s+.+",
            r"^отсортируй\s+(по|за)\s+.+",
        ],
        "intent": "navigate",
        "action": "open_search",
        "response": "Открываю фильтры поиска",
    },
    # ── Open specific category ──
    {
        "patterns": [
            r"^(открой|открыть|покажи|показать)\s+категори(?:ю|и)\s+(.+)$",
            r"^(открой|открыть)\s+(раздел|категорию)\s+(.+)$",
        ],
        "intent": "navigate",
        "action": "open_category",
        "response": "Открываю категорию",
    },
    # ── Show cards ──
    {
        "patterns": [
            r"^(покажи|показать|открой|открыть)\s+карточк(?:у|и)\s*(.*)$",
            r"^(покажи|показать)\s+подробнее\s+(о|про)\s+(.+)$",
        ],
        "intent": "navigate",
        "action": "show_cards",
        "response": "Показываю карточку",
    },
]

# ─── Simple response patterns (greetings, help, etc.) ─────

SIMPLE_RESPONSES: list[dict[str, Any]] = [
    {
        "patterns": [
            r"^(привет|здравствуй|здравствуйте|хай|хеллоу|hi|hello|hey|дарова|ку)$",
            r"^(доброе\s+утро|добрый\s+день|добрый\s+вечер)$",
        ],
        "intent": "chat",
        "response": "Привет! Я — AION, ваш AI-ассистент. Я помогаю находить услуги, бронировать, искать партнёров и управлять приложением. Спросите меня о чём угодно!",
    },
    {
        "patterns": [
            r"^(что\s+ты\s+умеешь|что\s+ты\s+можешь|твои\s+возможности|помощь|помоги|help|команды)$",
            r"^(как\s+работает|как\s+пользоваться|как\s+это\s+работает)$",
        ],
        "intent": "chat",
        "response": "Я могу:\n\n🏠 **Навигация** — открыть категории, профиль, избранное\n🔍 **Поиск** — найти партнёров, услуги, товары\n📅 **Бронирование** — записаться, заказать, забронировать\n💡 **Рекомендации** — подобрать лучшее для вас\n📋 **CRM** — проверить статус заказа, отменить бронь\n🧠 **Память** — запомнить ваши предпочтения\n\nПросто напишите, что вам нужно!",
    },
    {
        "patterns": [
            r"^(спасибо|благодарю|thanks|thank\s*you|thx)$",
        ],
        "intent": "chat",
        "response": "Пожалуйста! Обращайтесь, если ещё что-то понадобится 😊",
    },
    {
        "patterns": [
            r"^(пока|до\s+свидания|goodbye|bye|до\s+встречи|увидимся)$",
        ],
        "intent": "chat",
        "response": "До свидания! Буду рад помочь снова 👋",
    },
    {
        "patterns": [
            r"^(кто\s+ты|ты\s+кто|что\s+ты\s+такое|расскажи\s+о\s+себе)$",
        ],
        "intent": "chat",
        "response": "Я — AION, AI-операционная система для жизни. Я создан помогать людям за границей находить услуги, партнёров и решать бытовые вопросы. Работаю 24/7 и говорю на русском и английском.",
    },
]


def _normalize(text: str) -> str:
    """Normalize text: lowercase, strip, remove common filler words."""
    text = text.lower().strip()
    text = re.sub(r"[!?,.\-–—]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _match_patterns(text: str, patterns_list: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Try to match text against a list of pattern dictionaries."""
    normalized = _normalize(text)

    for entry in patterns_list:
        for pattern in entry["patterns"]:
            try:
                if re.search(pattern, normalized, re.IGNORECASE):
                    return entry
            except re.error:
                continue

    # Also try the raw text for patterns that might need original case
    for entry in patterns_list:
        for pattern in entry["patterns"]:
            try:
                if re.search(pattern, text.strip(), re.IGNORECASE):
                    return entry
            except re.error:
                continue

    return None


# ─── Category name mapping ────────────────────────────────

CATEGORY_ALIASES: dict[str, str] = {
    "недвижимость": "real_estate",
    "квартира": "real_estate",
    "квартиру": "real_estate",
    "дом": "real_estate",
    "виза": "visa",
    "визы": "visa",
    "транспорт": "transport",
    "такси": "transport",
    "машина": "transport",
    "медицина": "health",
    "врач": "health",
    "врача": "health",
    "стоматолог": "health",
    "терапевт": "health",
    "страхование": "insurance",
    "страховка": "insurance",
    "еда": "food",
    "доставка": "food",
    "ресторан": "food",
    "клининг": "cleaning",
    "уборка": "cleaning",
    "красота": "beauty",
    "салон": "beauty",
    "парикмахер": "beauty",
    "дети": "kids",
    "животные": "pets",
    "ветеринар": "pets",
    "экскурсии": "excursions",
    "спорт": "sports",
    "психология": "psychology",
    "фото": "photo",
    "цветы": "flowers",
    "мероприятия": "events",
    "образование": "education",
    "прокат": "rental",
    "ремонт": "repair",
    "обмен": "currency",
    "шопинг": "shopping",
    "помощь": "emergency",
}


def _extract_category(text: str) -> str | None:
    """Extract a category name from the text if present (word-boundary match)."""
    normalized = _normalize(text)
    for alias, category_id in CATEGORY_ALIASES.items():
        if re.search(r"\b" + re.escape(alias) + r"\b", normalized):
            return category_id
    return None


# ─── Public API ───────────────────────────────────────────


class CommandRouter:
    """Fast command router — matches user input against known patterns.

    Returns AgentResult immediately for recognized commands,
    or None if the input needs LLM-based processing.
    """

    @staticmethod
    def route(text: str) -> AgentResult | None:
        """Try to route a command without LLM.

        Args:
            text: Raw user message.

        Returns:
            AgentResult if command was matched, None if it needs LLM.
        """
        start = time.monotonic()

        # 1. Try navigation patterns
        match = _match_patterns(text, NAVIGATION_PATTERNS)
        if match:
            action = match["action"]
            response = match["response"]

            # Extract category if present (for open_category commands)
            params: dict[str, Any] = {}
            if action == "open_category":
                category = _extract_category(text)
                if category:
                    params["category"] = category
                    response = f"Открываю категорию {category}"

            latency = (time.monotonic() - start) * 1000  # microseconds → ms
            return AgentResult(
                response=response,
                navigation={
                    "action": action,
                    "params": params,
                    "source": "command_router",
                },
                latency_ms=latency,
            )

        # 2. Try simple responses (greetings, help, etc.)
        match = _match_patterns(text, SIMPLE_RESPONSES)
        if match:
            latency = (time.monotonic() - start) * 1000
            return AgentResult(
                response=match["response"],
                latency_ms=latency,
            )

        # 3. Not a simple command — needs LLM
        return None

    @staticmethod
    def is_simple_command(text: str) -> bool:
        """Quick check if the text is a simple command (no LLM needed)."""
        return _match_patterns(text, NAVIGATION_PATTERNS) is not None or \
               _match_patterns(text, SIMPLE_RESPONSES) is not None

    @staticmethod
    def pattern_count() -> int:
        """Total number of patterns across all command categories."""
        nav_count = sum(len(e["patterns"]) for e in NAVIGATION_PATTERNS)
        simple_count = sum(len(e["patterns"]) for e in SIMPLE_RESPONSES)
        return nav_count + simple_count
