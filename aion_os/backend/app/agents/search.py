"""Search Agent — finds services, partners, and information.

Responsibility:
- Execute RAG search across the knowledge base
- Search for partners by category/location/language
- Fallback to direct DB queries when RAG is unavailable
- Return formatted results with navigation cards and partner details
"""

from __future__ import annotations

import json
import time
from typing import Any

from sqlalchemy import select

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.db.session import async_session_factory
from app.models.partner import Partner
from app.rag.engine import RAGEngine


class SearchAgent(BaseAgent):
    """Searches the knowledge base and partner directory."""

    agent_name = "search"
    agent_description = "Finds services, partners, and information"

    EXTRACTION_PROMPT = """Извлеки параметры поиска из запроса пользователя.

Запрос: {message}

Ответь ТОЛЬКО в формате JSON:
{{
    "category": "категория или пустая строка",
    "subcategory": "подкатегория или пустая строка",
    "location": "город или пустая строка",
    "query": "ключевые слова для поиска",
    "languages": ["языки через запятую"]
}}
"""

    async def execute(self, ctx: AgentContext) -> AgentResult:
        start = time.monotonic()

        # 1. Extract search parameters using LLM
        params = await self._extract_params(ctx.message)
        category = params.get("category", "")
        subcategory = params.get("subcategory", "")
        location = params.get("location", "")
        search_query = params.get("query", ctx.message)

        # 2. Try RAG search first (requires pgvector/PostgreSQL)
        rag_results = []
        if ctx.session:
            try:
                rag = RAGEngine(ctx.session)
                rag_results = await rag.search(
                    query=search_query,
                    category=category or None,
                )
            except Exception:
                rag_results = []

        # 3. Search partners database directly
        partners = []
        if ctx.session:
            try:
                async with async_session_factory() as session:
                    query = select(Partner).where(Partner.is_active == True)

                    if category:
                        query = query.where(Partner.category.ilike(f"%{category}%"))
                    if subcategory:
                        query = query.where(Partner.subcategory.ilike(f"%{subcategory}%"))
                    if location:
                        query = query.where(Partner.city.ilike(f"%{location}%"))

                    query = query.order_by(Partner.rating.desc()).limit(10)
                    db_result = await session.execute(query)
                    partners = db_result.scalars().all()

                    # Filter by language if requested
                    requested_langs = params.get("languages", [])
                    if requested_langs and partners:
                        lang_filtered = []
                        for p in partners:
                            p_langs = json.loads(p.languages) if isinstance(p.languages, str) else []
                            if any(rl.lower() in str(p_langs).lower() for rl in requested_langs):
                                lang_filtered.append(p)
                        if lang_filtered:
                            partners = lang_filtered

            except Exception:
                partners = []

        # 4. Build context for LLM
        context_parts = []

        # Add RAG context if available
        if rag_results:
            rag_context = await rag.format_context(rag_results, max_chars=2000)
            if rag_context:
                context_parts.append(rag_context)

        # Add partner context
        if partners:
            partner_lines = []
            for p in partners:
                langs = json.loads(p.languages) if isinstance(p.languages, str) else []
                tags = json.loads(p.tags) if isinstance(p.tags, str) else []
                partner_lines.append(
                    f"- 🏪 {p.name} (⭐{p.rating}/5)\n"
                    f"  📍 {p.city}, {p.country} | 💰 {p.price_range}\n"
                    f"  🗣️  {', '.join(langs)}\n"
                    f"  🏷️  {', '.join(tags[:4])}\n"
                    f"  📞 {p.phone}\n"
                    f"  📝 {p.description[:200]}"
                )
            partner_context = "\n\n".join(partner_lines)
            context_parts.append(f"📋 Найденные партнёры ({len(partners)}):\n\n{partner_context}")

        full_context = "\n\n---\n\n".join(context_parts) if context_parts else ""

        # 5. Generate response with LLM
        if full_context:
            system_prompt = f"""Ты — поисковый ассистент AION. У тебя есть актуальные данные из базы партнёров.

ИНСТРУКЦИИ:
1. Отвечай на русском языке.
2. Используй информацию из базы данных ниже — там реальные партнёры с контактами.
3. Если данные есть — покажи их красиво, с рейтингом, телефоном, адресом.
4. Если данных нет — предложи пользователю уточнить запрос.
5. Всегда указывай контактные данные партнёров (телефон).

Категория поиска: {category or 'все'}
Локация: {location or 'не указана'}

Данные из базы:
{full_context}"""
        else:
            system_prompt = f"Ты — поисковый ассистент AION. Помоги пользователю найти нужные услуги. Категория: {category or 'все'}"

        response = await self._llm.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ctx.message},
        ])

        # 6. Build cards from partners
        cards = []
        for p in partners[:5]:
            langs = json.loads(p.languages) if isinstance(p.languages, str) else []
            cards.append({
                "id": p.id,
                "title": p.name,
                "description": p.description[:150],
                "category": p.category,
                "city": p.city,
                "rating": p.rating,
                "phone": p.phone,
                "price_range": p.price_range,
                "languages": langs,
            })

        latency = (time.monotonic() - start) * 1000
        self.log_agent_action(ctx, f"search:{category}", latency_ms=latency)

        return AgentResult(
            response=response.content,
            data={
                "partners_found": len(partners),
                "rag_results": len(rag_results),
                "partners": [{"id": p.id, "name": p.name, "phone": p.phone, "rating": p.rating} for p in partners],
            },
            cards=cards if cards else None,
            latency_ms=latency,
        )

    async def _extract_params(self, message: str) -> dict[str, Any]:
        """Extract search parameters from user message using LLM."""
        prompt = self.EXTRACTION_PROMPT.format(message=message[:300])
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
            return {"category": "", "subcategory": "", "location": "", "query": message, "languages": []}
