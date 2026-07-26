"""Partner Agent — finds, filters, and recommends service partners.

Responsibility:
- Search partners by category, location, language
- Filter by rating, price range, tags
- Show partner cards with details
- Recommend best matches
"""

from __future__ import annotations

import json
import time

from sqlalchemy import select

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.models.partner import Partner


class PartnerAgent(BaseAgent):
    """Finds and recommends service partners."""

    agent_name = "partner"
    agent_description = "Searches and recommends service partners"

    PARTNER_EXTRACT_PROMPT = """Извлеки параметры поиска партнёра из запроса.

Запрос: {message}

Ответь ТОЛЬКО в формате JSON:
{{
    "category": "категория услуг",
    "subcategory": "подкатегория или пусто",
    "city": "город или пусто",
    "language": "язык или пусто",
    "min_rating": 0.0,
    "max_price": 0
}}
"""

    async def execute(self, ctx: AgentContext) -> AgentResult:
        start = time.monotonic()

        # 1. Extract search params
        params = await self._extract_params(ctx.message)
        category = params.get("category", "")
        city = params.get("city", "")
        language = params.get("language", "")
        min_rating = params.get("min_rating", 0.0)

        partners = []
        if ctx.session:
            from app.db.session import async_session_factory

            async with async_session_factory() as session:
                query = select(Partner).where(Partner.is_active == True)

                if category:
                    query = query.where(Partner.category.ilike(f"%{category}%"))
                if city:
                    query = query.where(Partner.city.ilike(f"%{city}%"))
                if min_rating > 0:
                    query = query.where(Partner.rating >= min_rating)

                query = query.order_by(Partner.rating.desc()).limit(10)
                result = await session.execute(query)
                partners = result.scalars().all()

                # Filter by language (stored as JSON array string)
                if language and partners:
                    partners = [p for p in partners if language.lower() in p.languages.lower()]

        if not partners:
            response = await self._llm.chat([
                {"role": "system", "content": "Ты — ассистент по поиску партнёров AION. Партнёры не найдены. Предложи пользователю уточнить запрос или попробовать другую категорию."},
                {"role": "user", "content": ctx.message},
            ])
            return AgentResult(response=response.content, data={"partners_found": 0})

        # Format partner cards
        cards = []
        for p in partners[:5]:
            cards.append({
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "city": p.city,
                "rating": p.rating,
                "price_range": p.price_range,
                "phone": p.phone,
                "languages": json.loads(p.languages) if isinstance(p.languages, str) else [],
                "description": p.description[:200],
            })

        # Generate response
        partners_text = "\n\n".join(
            f"🏪 {p.name}\n📂 {p.category}\n⭐ {p.rating}/5\n📍 {p.city}\n📞 {p.phone}\n{p.description[:200]}"
            for p in partners[:3]
        )

        response = await self._llm.chat([
            {"role": "system", "content": f"""Ты — ассистент по поиску партнёров AION.
Найдено {len(partners)} партнёров. Рекомендуй лучших.

Партнёры:
{partners_text}"""},
            {"role": "user", "content": ctx.message},
        ])

        latency_ms = (time.monotonic() - start) * 1000
        self.log_agent_action(ctx, f"partner_search:{category}", latency_ms=latency_ms)

        return AgentResult(
            response=response.content,
            cards=cards,
            data={"partners_found": len(partners), "partners": cards},
            latency_ms=latency_ms,
        )

    async def _extract_params(self, message: str) -> dict:
        prompt = self.PARTNER_EXTRACT_PROMPT.format(message=message[:300])
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
            return {"category": "", "subcategory": "", "city": "", "language": "", "min_rating": 0, "max_price": 0}
