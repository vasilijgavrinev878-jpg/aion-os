"""Database session and engine management.

Supports both PostgreSQL+pgvector (production) and SQLite (development/testing).
Engine is lazy-initialized to support cross-platform test mode detection.
Exposes get_session_factory() function instead of module-level variable.
"""

from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


_engine = None
_session_factory = None


def _is_test_mode() -> bool:
    """Check if running in test/dev mode (no PostgreSQL)."""
    return os.environ.get("AION_TEST_MODE", "0") == "1"


def _get_database_url() -> str:
    """Get the appropriate database URL based on environment."""
    if _is_test_mode():
        return "sqlite+aiosqlite:///./aion_test.db"
    return settings.DATABASE_URL


def _get_engine():
    """Get or create the async engine (lazy initialization)."""
    global _engine
    if _engine is None:
        url = _get_database_url()
        connect_args = {"check_same_thread": False} if _is_test_mode() else {}
        _engine = create_async_engine(
            url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
    return _engine


def _get_session_factory():
    """Get or create the session factory (lazy initialization)."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            _get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


def get_session_factory():
    """Public accessor for the async session factory.
    
    Compatible with code that imports async_session_factory as module-level name.
    """
    return _get_session_factory()


# Backward compatibility: allow `from app.db.session import async_session_factory`
async_session_factory = _get_session_factory()


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: yield an async database session."""
    factory = _get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables. Uses SQLAlchemy metadata for dev, Alembic for production."""
    engine = _get_engine()
    async with engine.begin() as conn:
        from app.models.user import User  # noqa: F401
        from app.models.memory import UserMemory  # noqa: F401
        from app.models.agent import AgentLog  # noqa: F401
        from app.models.booking import Booking  # noqa: F401
        from app.models.partner import Partner  # noqa: F401

        await conn.run_sync(Base.metadata.create_all)

    if settings.DEBUG:
        print("  ✅ Database tables created")


async def close_db() -> None:
    """Dispose of the database engine."""
    global _engine, _session_factory
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
