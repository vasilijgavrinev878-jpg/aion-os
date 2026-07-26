"""User memory database model — for long-term preferences and history."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class UserMemory(Base):
    """Long-term user memory — preferences, facts, history summaries."""

    __tablename__ = "user_memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)

    # Memory type: preference, fact, summary, preference_category, recent_action
    memory_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    # Key-value storage
    memory_key: Mapped[str] = mapped_column(String(256), nullable=False)
    memory_value: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Relevance score (0-1) for decay
    relevance: Mapped[float] = mapped_column(Float, default=1.0)

    # Metadata
    source: Mapped[str] = mapped_column(String(64), default="chat")  # chat, system, agent
    ttl_days: Mapped[int] = mapped_column(Integer, default=365)  # Time-to-live

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<UserMemory {self.memory_type}:{self.memory_key}>"
