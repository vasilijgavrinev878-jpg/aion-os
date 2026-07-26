"""Telegram InitData verification and JWT authentication."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── Telegram InitData Verification ──────────────────────


class TelegramUser(BaseModel):
    """Verified Telegram user data from InitData."""
    id: int
    first_name: str = ""
    last_name: str = ""
    username: str = ""
    language_code: str = "en"
    is_premium: bool = False
    photo_url: str = ""
    auth_date: int = 0


def verify_telegram_init_data(init_data: str) -> TelegramUser | None:
    """Verify Telegram Mini App initData using HMAC-SHA256.

    Args:
        init_data: Raw query string from Telegram.WebApp.initData.

    Returns:
        TelegramUser if valid, None if tampered or expired.
    """
    try:
        # Parse the query string
        params = {}
        for pair in init_data.split("&"):
            if "=" not in pair:
                continue
            key, value = pair.split("=", 1)
            params[key] = value

        received_hash = params.pop("hash", None)
        if not received_hash:
            return None

        # Sort, join, and create data check string
        sorted_params = sorted(
            (k, v) for k, v in params.items()
        )
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_params)

        # Create secret key: HMAC-SHA256(bot_token, "WebAppData")
        secret_key = hmac.new(
            settings.telegram_bot_token_bytes,
            b"WebAppData",
            hashlib.sha256,
        ).digest()

        # Compute expected hash
        computed_hash = hmac.new(
            secret_key,
            data_check_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if computed_hash != received_hash:
            return None

        # Check auth_date is recent (within 1 day)
        auth_date = int(params.get("auth_date", 0))
        if time.time() - auth_date > 86400:
            return None

        # Parse user
        user_data = params.get("user", "{}")
        user_json = json.loads(user_data)

        return TelegramUser(
            id=user_json.get("id", 0),
            first_name=user_json.get("first_name", ""),
            last_name=user_json.get("last_name", ""),
            username=user_json.get("username", ""),
            language_code=user_json.get("language_code", "en"),
            is_premium=user_json.get("is_premium", False),
            photo_url=user_json.get("photo_url", ""),
            auth_date=auth_date,
        )

    except (ValueError, KeyError, json.JSONDecodeError):
        return None


# ─── JWT ──────────────────────────────────────────────────


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None


# ─── Password Hashing ─────────────────────────────────────


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)
