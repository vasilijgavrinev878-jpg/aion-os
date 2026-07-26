"""User database model."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(128), default="")
    last_name: Mapped[str] = mapped_column(String(128), default="")
    username: Mapped[str] = mapped_column(String(128), default="")
    language_code: Mapped[str] = mapped_column(String(10), default="en")
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    photo_url: Mapped[str] = mapped_column(String(512), default="")

    # Preferences
    preferred_categories: Mapped[str] = mapped_column(Text, default="[]")
    preferred_city: Mapped[str] = mapped_column(String(128), default="")

    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} @{self.username}>"
