"""Booking database model."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    partner_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Service info
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    service_name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")

    # Status: pending, confirmed, in_progress, completed, cancelled
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)

    # Scheduling
    preferred_date: Mapped[str] = mapped_column(String(32), default="")
    preferred_time: Mapped[str] = mapped_column(String(16), default="")

    # Price
    price: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(8), default="USD")

    # Contact info
    contact_name: Mapped[str] = mapped_column(String(128), default="")
    contact_phone: Mapped[str] = mapped_column(String(32), default="")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Booking #{self.id} {self.category}:{self.service_name} [{self.status}]>"
