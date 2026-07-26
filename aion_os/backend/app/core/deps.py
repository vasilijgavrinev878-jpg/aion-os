"""FastAPI dependencies — auth, session, rate limiting."""

from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import TelegramUser, decode_access_token, verify_telegram_init_data
from app.db.session import get_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: get database session."""
    async for session in get_session():
        yield session


async def verify_telegram_auth(
    authorization: str = Header(None, description="Telegram InitData or JWT Bearer token"),
) -> TelegramUser:
    """Dependency: verify Telegram authentication.

    Accepts either:
    1. Bearer JWT token (from previous auth)
    2. Raw Telegram InitData query string
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
        )

    # Try JWT Bearer token first
    if authorization.startswith("Bearer "):
        token = authorization[7:]
        payload = decode_access_token(token)
        if payload and "user_id" in payload:
            return TelegramUser(
                id=payload["user_id"],
                first_name=payload.get("first_name", ""),
                username=payload.get("username", ""),
                language_code=payload.get("lang", "en"),
            )

    # Fall back to raw Telegram InitData
    user = verify_telegram_init_data(authorization)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Telegram InitData",
        )

    return user


async def get_current_user_id(
    auth: TelegramUser = Depends(verify_telegram_auth),
) -> int:
    """Dependency: get current user's Telegram ID."""
    return auth.id
