"""Security utilities — encryption, rate limiting, etc."""

from __future__ import annotations

import secrets
from typing import Any

from cryptography.fernet import Fernet
from fastapi import HTTPException, Request, status


def generate_fernet_key() -> str:
    """Generate a new Fernet encryption key."""
    return Fernet.generate_key().decode()


class DataEncryptor:
    """Symmetric encryption for sensitive data at rest."""

    def __init__(self, key: str | None = None) -> None:
        self._fernet = Fernet(
            key.encode() if key else generate_fernet_key().encode()
        )

    def encrypt(self, data: str) -> str:
        """Encrypt a string."""
        return self._fernet.encrypt(data.encode()).decode()

    def decrypt(self, token: str) -> str:
        """Decrypt a token back to string."""
        return self._fernet.decrypt(token.encode()).decode()


def generate_api_key() -> str:
    """Generate a secure random API key."""
    return f"aion_{secrets.token_hex(32)}"


def sanitize_input(text: str) -> str:
    """Basic input sanitization — strip control chars."""
    return "".join(c for c in text if c.isprintable() or c in "\n\r\t")


class RateLimiter:
    """Simple in-memory rate limiter (use Redis in production)."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60) -> None:
        self._max = max_requests
        self._window = window_seconds
        self._buckets: dict[str, list[float]] = {}

    async def check(self, key: str) -> bool:
        """Check if request is allowed. True = allowed."""
        import time
        now = time.time()
        window_start = now - self._window

        if key not in self._buckets:
            self._buckets[key] = []

        # Prune old entries
        self._buckets[key] = [
            t for t in self._buckets[key] if t > window_start
        ]

        if len(self._buckets[key]) >= self._max:
            return False

        self._buckets[key].append(now)
        return True


async def verify_rate_limit(request: Request) -> None:
    """Dependency: rate limit by client IP."""
    client_ip = request.client.host if request.client else "unknown"
    limiter = RateLimiter()
    if not await limiter.check(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please slow down.",
        )
