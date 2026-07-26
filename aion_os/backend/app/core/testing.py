"""Testing utilities — enables running the app without PostgreSQL.

In testing/development mode, uses SQLite instead of PostgreSQL.
pgvector features (RAG search) will gracefully degrade.
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.session import Base


@pytest.fixture
async def db_session():
    """Create a test SQLite in-memory database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


def is_test_mode() -> bool:
    """Check if running in test/dev mode (no PostgreSQL)."""
    return os.environ.get("AION_TEST_MODE", "0") == "1"


def get_database_url() -> str:
    """Get appropriate database URL based on environment.

    Returns SQLite for test/dev, PostgreSQL for production.
    """
    if is_test_mode():
        return "sqlite+aiosqlite:///./aion_test.db"
    from app.config import settings
    return settings.DATABASE_URL


def get_sync_database_url() -> str:
    """Get sync database URL for Alembic/scripts."""
    if is_test_mode():
        return "sqlite+aiosqlite:///./aion_test.db"
    from app.config import settings
    return settings.DATABASE_URL_SYNC
