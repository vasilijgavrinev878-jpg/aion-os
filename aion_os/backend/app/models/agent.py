"""Agent log database model — for monitoring and debugging."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AgentLog(Base):
    """Agent execution log for monitoring."""

    __tablename__ = "agent_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)

    # Agent info
    agent_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="success")  # success, error, pending

    # Input/output
    input_data: Mapped[str] = mapped_column(Text, default="")
    output_data: Mapped[str] = mapped_column(Text, default="")

    # Performance
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    model: Mapped[str] = mapped_column(String(64), default="")

    # Session tracking
    conversation_id: Mapped[str] = mapped_column(String(64), default="", index=True)

    # Error tracking
    error_message: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<AgentLog {self.agent_name}:{self.action} [{self.status}]>"
