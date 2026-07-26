"""Short-term conversation store — Redis-based with in-memory fallback.

Automatically falls back to in-memory storage when Redis is unavailable
(e.g., during development without Docker).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger("aion.memory.store")


class ConversationStore:
    """Stores recent conversation history.

    Primary: Redis for production (TTL-based, fast retrieval).
    Fallback: In-memory dict when Redis is unavailable (dev/test).
    """

    def __init__(self) -> None:
        self._redis: aioredis.Redis | None = None
        self._ttl = 86400  # 24 hours
        self._use_redis = True
        self._memory_store: dict[str, list[dict[str, Any]]] = {}  # In-memory fallback
        self._redis_available: bool | None = None  # Cached availability check

    async def _is_redis_available(self) -> bool:
        """Check if Redis is reachable (cached after first attempt)."""
        if self._redis_available is not None:
            return self._redis_available

        try:
            import socket
            host = settings.REDIS_HOST
            port = settings.REDIS_PORT
            sock = socket.create_connection((host, port), timeout=1.0)
            sock.close()
            self._redis_available = True
        except (socket.timeout, ConnectionRefusedError, OSError):
            self._redis_available = False
            logger.warning("Redis unavailable — using in-memory conversation store")
        return self._redis_available

    async def add_message(
        self,
        user_id: int,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add a message to the conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }

        if await self._is_redis_available():
            try:
                r = await self._get_redis()
                key = f"conversation:{user_id}"
                await r.rpush(key, json.dumps(message, ensure_ascii=False))
                await r.expire(key, self._ttl)

                max_len = settings.MEMORY_MAX_HISTORY
                current_len = await r.llen(key)
                if current_len > max_len:
                    await r.ltrim(key, current_len - max_len, -1)
                return
            except Exception as e:
                logger.warning(f"Redis add_message failed, falling back to memory: {e}")
                self._redis_available = False

        # In-memory fallback
        key = f"conversation:{user_id}"
        if key not in self._memory_store:
            self._memory_store[key] = []
        self._memory_store[key].append(message)
        # Trim
        max_len = settings.MEMORY_MAX_HISTORY
        if len(self._memory_store[key]) > max_len:
            self._memory_store[key] = self._memory_store[key][-max_len:]

    async def get_history(
        self,
        user_id: int,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Get recent conversation history."""
        if await self._is_redis_available():
            try:
                r = await self._get_redis()
                key = f"conversation:{user_id}"
                messages = await r.lrange(key, -limit, -1)
                result = []
                for msg in messages:
                    try:
                        result.append(json.loads(msg))
                    except json.JSONDecodeError:
                        continue
                return result
            except Exception as e:
                logger.warning(f"Redis get_history failed, falling back to memory: {e}")
                self._redis_available = False

        # In-memory fallback
        key = f"conversation:{user_id}"
        if key not in self._memory_store:
            return []
        return self._memory_store[key][-limit:]

    async def format_as_messages(
        self,
        user_id: int,
        system_prompt: str,
        limit: int = 10,
    ) -> list[dict[str, str]]:
        """Format conversation as LLM messages (with system prompt)."""
        history = await self.get_history(user_id, limit)
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
            })
        return messages

    async def clear(self, user_id: int) -> None:
        """Clear conversation history for a user."""
        if await self._is_redis_available():
            try:
                r = await self._get_redis()
                await r.delete(f"conversation:{user_id}")
                return
            except Exception:
                self._redis_available = False

        key = f"conversation:{user_id}"
        if key in self._memory_store:
            del self._memory_store[key]

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            try:
                await self._redis.close()
            except Exception:
                pass
            self._redis = None

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
            )
        return self._redis
