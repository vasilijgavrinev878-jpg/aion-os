"""CRM Agent — manages orders, tickets, and customer relationships.

Responsibility:
- List user's orders/bookings
- Update order status
- Create support tickets
- Show order history
"""

from __future__ import annotations

import json
import time

from sqlalchemy import select

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.models.booking import Booking


class CRMAgent(BaseAgent):
    """Manages orders, tickets, and customer relationships."""

    agent_name = "crm"
    agent_description = "Manages orders, bookings, and support tickets"

    CRM_PROMPT = """Определи CRM-действие из запроса пользователя.

Сообщение: {message}

Действия:
- list_orders: Показать заказы/бронирования
- order_status: Узнать статус заказа
- cancel_order: Отменить заказ
- create_ticket: Создать обращение в поддержку
- contact_partner: Связаться с партнёром

Ответь ТОЛЬКО в формате JSON:
{{"action": "list_orders|order_status|cancel_order|create_ticket|contact_partner", "order_id": 0, "reason": ""}}
"""

    async def execute(self, ctx: AgentContext) -> AgentResult:
        start = time.monotonic()
        action_info = await self._classify_action(ctx.message)
        action = action_info.get("action", "list_orders")
        order_id = action_info.get("order_id", 0)

        if action == "list_orders":
            return await self._list_orders(ctx, start)
        elif action == "order_status" and order_id:
            return await self._order_status(ctx, order_id, start)
        elif action == "cancel_order" and order_id:
            return await self._cancel_order(ctx, order_id, start)
        else:
            # General CRM response via LLM
            ctx.metadata["action"] = action
            response = await self._llm.chat([
                {"role": "system", "content": "Ты — CRM-ассистент AION. Помогаешь с заказами, бронированиями и обращениями."},
                {"role": "user", "content": ctx.message},
            ])
            return AgentResult(response=response.content)

    async def _list_orders(self, ctx: AgentContext, start: float) -> AgentResult:
        if not ctx.session:
            return AgentResult(response="Сервис заказов временно недоступен.")

        from app.db.session import async_session_factory
        async with async_session_factory() as session:
            result = await session.execute(
                select(Booking).where(Booking.user_id == ctx.user_id).order_by(Booking.created_at.desc()).limit(10)
            )
            bookings = result.scalars().all()

        if not bookings:
            response = "У вас пока нет заказов. Хотите что-то забронировать?"
        else:
            lines = [f"📋 Ваши заказы ({len(bookings)}):"]
            for b in bookings:
                lines.append(f"• #{b.id} {b.service_name} — {b.status} ({b.created_at.strftime('%d.%m')})")
            response = "\n".join(lines)

        latency_ms = (time.monotonic() - start) * 1000
        self.log_agent_action(ctx, "crm_list_orders", latency_ms=latency_ms)
        return AgentResult(response=response, data={"bookings": [str(b) for b in bookings]}, latency_ms=latency_ms)

    async def _order_status(self, ctx: AgentContext, order_id: int, start: float) -> AgentResult:
        if not ctx.session:
            return AgentResult(response="Сервис заказов временно недоступен.")

        from app.db.session import async_session_factory
        async with async_session_factory() as session:
            result = await session.execute(
                select(Booking).where(Booking.id == order_id, Booking.user_id == ctx.user_id)
            )
            booking = result.scalar_one_or_none()

        if not booking:
            response = f"Заказ #{order_id} не найден."
        else:
            response = f"📋 Заказ #{booking.id}\n• Услуга: {booking.service_name}\n• Категория: {booking.category}\n• Статус: {booking.status}\n• Дата: {booking.created_at.strftime('%d.%m.%Y %H:%M')}"

        latency_ms = (time.monotonic() - start) * 1000
        return AgentResult(response=response, latency_ms=latency_ms)

    async def _cancel_order(self, ctx: AgentContext, order_id: int, start: float) -> AgentResult:
        if not ctx.session:
            return AgentResult(response="Сервис заказов временно недоступен.")

        from app.db.session import async_session_factory
        from app.models.booking import Booking
        from sqlalchemy import update

        async with async_session_factory() as session:
            await session.execute(
                update(Booking).where(
                    Booking.id == order_id,
                    Booking.user_id == ctx.user_id,
                ).values(status="cancelled")
            )
            await session.commit()

        latency_ms = (time.monotonic() - start) * 1000
        self.log_agent_action(ctx, f"crm_cancel:{order_id}", latency_ms=latency_ms)
        return AgentResult(response=f"✅ Заказ #{order_id} отменён.", latency_ms=latency_ms)

    async def _classify_action(self, message: str) -> dict:
        prompt = self.CRM_PROMPT.format(message=message[:300])
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
            return {"action": "list_orders", "order_id": 0, "reason": ""}
