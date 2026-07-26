"""Booking Agent — handles service bookings and reservations.

Responsibility:
- Create new bookings
- Check availability
- Modify/cancel bookings
- Confirm booking details with user
"""

from __future__ import annotations

import json
import time

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.models.booking import Booking


class BookingAgent(BaseAgent):
    """Handles service bookings, reservations, and scheduling."""

    agent_name = "booking"
    agent_description = "Creates and manages service bookings"

    BOOKING_EXTRACT_PROMPT = """Извлеки данные для бронирования из запроса пользователя.

Запрос: {message}

Ответь ТОЛЬКО в формате JSON:
{{
    "category": "категория услуги",
    "service_name": "название услуги",
    "description": "описание",
    "preferred_date": "желаемая дата или пусто",
    "preferred_time": "желаемое время или пусто",
    "partner_id": 0,
    "contact_name": "имя или пусто",
    "contact_phone": "телефон или пусто"
}}
"""

    async def execute(self, ctx: AgentContext) -> AgentResult:
        start = time.monotonic()

        # 1. Extract booking details
        details = await self._extract_booking_details(ctx.message)

        if not details or not details.get("category"):
            # Ask for more details
            response = await self._llm.chat([
                {"role": "system", "content": """Ты — ассистент по бронированию AION.
Уточни у пользователя детали бронирования:
- Какую услугу он хочет забронировать
- Категория услуги
- Желаемая дата и время
- Контактные данные"""},
                {"role": "user", "content": ctx.message},
            ])
            return AgentResult(response=response.content, should_escalate=True)

        # 2. Create booking in database
        if ctx.session:
            from app.db.session import async_session_factory

            booking = Booking(
                user_id=ctx.user_id,
                partner_id=details.get("partner_id", 0),
                category=details.get("category", ""),
                service_name=details.get("service_name", "Услуга"),
                description=details.get("description", ""),
                status="pending",
                preferred_date=details.get("preferred_date", ""),
                preferred_time=details.get("preferred_time", ""),
                contact_name=details.get("contact_name", ctx.user_name),
                contact_phone=details.get("contact_phone", ""),
            )

            async with async_session_factory() as session:
                session.add(booking)
                await session.commit()
                await session.refresh(booking)

                latency = (time.monotonic() - start) * 1000
                self.log_agent_action(ctx, "booking_created", latency_ms=latency)

                return AgentResult(
                    response=f"✅ Заявка на бронирование #{booking.id} создана!\n"
                             f"• Услуга: {booking.service_name}\n"
                             f"• Категория: {booking.category}\n"
                             f"• Дата: {booking.preferred_date or 'уточняется'}\n"
                             f"• Статус: {booking.status}\n\n"
                             f"Мы свяжемся с вами для подтверждения.",
                    data={"booking_id": booking.id, "status": booking.status},
                    latency_ms=latency,
                )

        return AgentResult(response="Извините, сервис бронирования временно недоступен.")

    async def _extract_booking_details(self, message: str) -> dict:
        """Extract booking details from user message."""
        prompt = self.BOOKING_EXTRACT_PROMPT.format(message=message[:400])
        try:
            response = await self._llm.chat([
                {"role": "user", "content": prompt},
            ], temperature=0.1, max_tokens=250)
            text = response.content.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception:
            return {}
