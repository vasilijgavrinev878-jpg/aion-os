"""Knowledge Agent — answers questions from the knowledge base.

Responsibility:
- Answer questions about AION project, categories, services
- Provide information from documentation, FAQ, and bibles
- Explain how things work
"""

from __future__ import annotations

import time

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.rag.engine import RAGEngine


class KnowledgeAgent(BaseAgent):
    """Answers questions from the AION knowledge base."""

    agent_name = "knowledge"
    agent_description = "Answers questions about AION from documentation"

    async def execute(self, ctx: AgentContext) -> AgentResult:
        start = time.monotonic()

        if ctx.session:
            rag = RAGEngine(ctx.session)
            results = await rag.search(ctx.message, top_k=3)
            context = await rag.format_context(results, max_chars=3000)

            system_prompt = f"""Ты — база знаний AION. Отвечай на вопросы о проекте используя информацию ниже.
Будь точным и ссылайся на источники. Если не знаешь — скажи честно.

Контекст:
{context}"""

        else:
            system_prompt = "Ты — база знаний AION. Отвечай на вопросы о проекте AION: 23 категории услуг, AI + операторы, Telegram Mini App, города присутствия."

        response = await self._llm.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ctx.message},
        ])

        latency = (time.monotonic() - start) * 1000
        self.log_agent_action(ctx, "knowledge_query", latency_ms=latency)

        return AgentResult(response=response.content, latency_ms=latency)
