"""AION OS Backend — Main FastAPI Application.

Entry point for the AI Operating System backend server.
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup/shutdown events."""
    # Startup
    logger = logging.getLogger("aion")
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    logger.info(f"   LLM Provider: {settings.LLM_DEFAULT_PROVIDER}")
    logger.info(f"   Database: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")

    # Initialize database (create tables in dev)
    if settings.DEBUG:
        from app.db.session import init_db
        try:
            await init_db()
            logger.info("   Database tables created/verified")
        except Exception as e:
            logger.warning(f"   Database init skipped: {e}")

    yield

    # Shutdown
    from app.db.session import close_db
    await close_db()
    logger.info("👋 AION OS shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Operating System for Telegram Mini App — AION",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── Middleware ─────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    start = time.monotonic()
    response = await call_next(request)
    duration = (time.monotonic() - start) * 1000
    logger = logging.getLogger("aion.http")
    logger.info(
        f"{request.method} {request.url.path} "
        f"→ {response.status_code} ({duration:.0f}ms)"
    )
    return response


# ─── Routes ────────────────────────────────────────────────

from app.api.rest import router as rest_router
from app.api.websocket import router as ws_router
from app.api.streaming import router as streaming_router

app.include_router(rest_router)
app.include_router(ws_router)
app.include_router(streaming_router)


# ─── Health ────────────────────────────────────────────────


@app.get("/")
async def root():
    """Root endpoint — API info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
    }


# ─── Logging ──────────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

# ─── Error Handlers ───────────────────────────────────────


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler — log and return 500."""
    logger = logging.getLogger("aion.error")
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )
