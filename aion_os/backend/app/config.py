"""Application configuration via environment variables."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── App ────────────────────────────────────────────
    APP_NAME: str = "AION OS"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ─── Telegram ───────────────────────────────────────
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_USERNAME: str = "aion_os_bot"

    @property
    def telegram_bot_token_bytes(self) -> bytes:
        return self.TELEGRAM_BOT_TOKEN.encode("utf-8")

    # ─── Database ───────────────────────────────────────
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "aion"
    POSTGRES_USER: str = "aion"
    POSTGRES_PASSWORD: str = "changeme_in_production"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ─── Redis ──────────────────────────────────────────
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    @property
    def REDIS_URL(self) -> str:
        pw = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{pw}{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # ─── JWT ────────────────────────────────────────────
    JWT_SECRET_KEY: str = "changeme_in_production_generate_random_64_chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ─── LLM ────────────────────────────────────────────
    LLM_DEFAULT_PROVIDER: Literal["deepseek", "qwen", "llama", "openai"] = "deepseek"
    LLM_DEFAULT_MODEL: str = "deepseek-chat"

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"

    QWEN_API_BASE: str = "http://llm:8000/v1"
    QWEN_MODEL: str = "qwen3-32b"

    LLAMA_API_BASE: str = "http://ollama:11434/v1"
    LLAMA_MODEL: str = "llama3.1:70b"

    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.groq.com/openai/v1"
    OPENAI_MODEL: str = "llama-3.3-70b-versatile"

    # ─── Embeddings ─────────────────────────────────────
    EMBEDDINGS_MODEL: str = "BAAI/bge-m3"
    EMBEDDINGS_DIMENSIONS: int = 1024
    EMBEDDINGS_API_BASE: str = "http://embeddings:8001/v1"

    # ─── Voice ──────────────────────────────────────────
    STT_MODEL: str = "whisper-large-v3-turbo"
    TTS_MODEL: str = "kokoro-82m"
    TTS_VOICE: str = "af_bella"
    TTS_SPEED: float = 1.0

    # ─── RAG ────────────────────────────────────────────
    RAG_CHUNK_SIZE: int = 512
    RAG_CHUNK_OVERLAP: int = 64
    RAG_TOP_K: int = 5
    RAG_SCORE_THRESHOLD: float = 0.65

    # ─── Memory ─────────────────────────────────────────
    MEMORY_MAX_HISTORY: int = 100
    MEMORY_SUMMARY_INTERVAL: int = 10

    # ─── WebSocket ──────────────────────────────────────
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 10000

    # ─── Admin ──────────────────────────────────────────
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme_in_production"
    ADMIN_SECRET_KEY: str = "changeme_in_production"


settings = Settings()

# Override from environment for docker-compose
for key in dir(settings):
    if key.startswith("TELEGRAM_") or key.startswith("POSTGRES_") or key.startswith("JWT_"):
        env_val = os.environ.get(key)
        if env_val:
            setattr(settings, key, env_val)
