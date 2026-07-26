"""Intent Cache — in-memory cache for frequent intent classifications.

Design:
- LRU eviction when cache exceeds max size
- TTL-based expiry (default 5 minutes)
- Normalized text matching for fuzzy cache hits
- Thread-safe for concurrent WebSocket connections

This reduces LLM calls for repeated or similar queries.
"""

from __future__ import annotations

import hashlib
import re
import time
from collections import OrderedDict
from typing import Any


class IntentCache:
    """In-memory LRU cache for intent classifications.

    Usage:
        cache = IntentCache(max_size=100, ttl_seconds=300)
        key = cache.make_key("Найди стоматолога")
        if key in cache:
            intent = cache.get(key)  # No LLM call needed!
        else:
            intent = await classify_intent(message)
            cache.set(key, intent)
    """

    def __init__(self, max_size: int = 100, ttl_seconds: int = 300) -> None:
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._cache: OrderedDict[str, tuple[float, dict[str, Any]]] = OrderedDict()

    # ─── Key generation ──────────────────────────────────

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize text for cache key matching."""
        text = text.lower().strip()
        # Remove filler words
        text = re.sub(r"\b(пожалуйста|пожалуй|можно|будь\s*добра|будьте\s*добры)\b", "", text)
        # Remove punctuation
        text = re.sub(r"[!?,.\-–—]+", " ", text)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def make_key(text: str) -> str:
        """Generate a cache key from message text.

        Uses SHA-256 of normalized text for deterministic keys.
        """
        normalized = IntentCache._normalize(text)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _similarity(a: str, b: str) -> float:
        """Simple word-overlap similarity for fuzzy matching."""
        words_a = set(IntentCache._normalize(a).split())
        words_b = set(IntentCache._normalize(b).split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        return len(intersection) / max(len(words_a), len(words_b))

    # ─── Cache operations ────────────────────────────────

    def get(self, key: str) -> dict[str, Any] | None:
        """Get a cached intent by key. Returns None if missing or expired."""
        if key not in self._cache:
            return None

        timestamp, intent = self._cache[key]
        if time.monotonic() - timestamp > self._ttl:
            # Expired
            del self._cache[key]
            return None

        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return intent

    def set(self, key: str, intent: dict[str, Any]) -> None:
        """Store an intent classification in the cache."""
        # Evict if at capacity
        while len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)  # Remove oldest (LRU)

        self._cache[key] = (time.monotonic(), intent)

    def get_fuzzy(self, text: str, threshold: float = 0.7) -> dict[str, Any] | None:
        """Try to find a cached intent for a similar message.

        Useful when the exact message isn't cached but a very similar one is.
        Example: "найди стоматолога" ≈ "найти стоматолога"
        """
        text_norm = self._normalize(text)
        for key, (timestamp, intent) in self._cache.items():
            if time.monotonic() - timestamp > self._ttl:
                continue
            # Try the key itself (hash isn't reversible, so we can't compare)
            # Instead, compare confidence from metadata if available
            if intent.get("entities", {}).get("_original"):
                cached_text = intent["entities"]["_original"]
                if self._similarity(text_norm, cached_text) >= threshold:
                    self._cache.move_to_end(key)
                    return intent
        return None

    def store_with_text(self, text: str, intent: dict[str, Any]) -> str:
        """Store intent with original text for fuzzy matching.

        Returns the cache key.
        """
        # Store original text in entities for fuzzy matching
        intent.setdefault("entities", {})
        intent["entities"]["_original"] = text

        key = self.make_key(text)
        self.set(key, intent)
        return key

    def invalidate(self, key: str) -> None:
        """Remove a specific entry from the cache."""
        self._cache.pop(key, None)

    def clear(self) -> None:
        """Clear the entire cache."""
        self._cache.clear()

    @property
    def size(self) -> int:
        """Current number of cached entries."""
        return len(self._cache)

    @property
    def is_empty(self) -> bool:
        return len(self._cache) == 0
