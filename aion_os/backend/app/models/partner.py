"""Partner/service provider database model."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Partner(Base):
    __tablename__ = "partners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    subcategory: Mapped[str] = mapped_column(String(64), default="")

    # Contact
    phone: Mapped[str] = mapped_column(String(32), default="")
    email: Mapped[str] = mapped_column(String(256), default="")
    address: Mapped[str] = mapped_column(String(512), default="")
    city: Mapped[str] = mapped_column(String(128), default="", index=True)
    country: Mapped[str] = mapped_column(String(64), default="")

    # Languages the partner speaks
    languages: Mapped[str] = mapped_column(String(256), default="[]")

    # Rating & pricing
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    price_range: Mapped[str] = mapped_column(String(32), default="")
    currency: Mapped[str] = mapped_column(String(8), default="USD")

    # Description
    description: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[str] = mapped_column(String(512), default="[]")  # JSON array

    # Geo
    latitude: Mapped[float] = mapped_column(Float, default=0.0)
    longitude: Mapped[float] = mapped_column(Float, default=0.0)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Embedding vector (stored in pgvector)
    # This is a virtual column — pgvector handles it separately

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Partner #{self.id} {self.name} [{self.category}]>"
