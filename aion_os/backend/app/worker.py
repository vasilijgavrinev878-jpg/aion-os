"""Background worker — processes async tasks via Redis queues.

Handles:
- Knowledge base ingestion
- Embedding generation
- Memory summarization
- Notification delivery
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import redis.asyncio as aioredis

from app.config import settings
from app.db.session import async_session_factory
from app.memory.manager import MemoryManager
from app.memory.store import ConversationStore
from app.rag.ingestion import IngestionService

logger = logging.getLogger("aion.worker")


async def process_task(task: dict) -> None:
    """Process a single background task."""
    task_type = task.get("type", "")
    data = task.get("data", {})

    logger.info(f"Processing task: {task_type}")

    try:
        async with async_session_factory() as session:
            if task_type == "ingest_knowledge":
                service = IngestionService(session)
                filepath = data.get("filepath", "")
                if filepath:
                    count = await service.ingest_file(filepath)
                    logger.info(f"Ingested {count} chunks from {filepath}")

            elif task_type == "ingest_directory":
                service = IngestionService(session)
                directory = data.get("directory", "")
                if directory:
                    results = await service.ingest_directory(directory)
                    logger.info(f"Ingested directory: {results}")

            elif task_type == "summarize_memory":
                user_id = data.get("user_id", 0)
                if user_id:
                    store = ConversationStore()
                    history = await store.get_history(user_id, 20)
                    if history:
                        from app.memory.summarizer import ConversationSummarizer
                        summarizer = ConversationSummarizer()
                        summary = await summarizer.summarize(history)
                        if summary:
                            mgr = MemoryManager()
                            await mgr._store_fact(user_id, {
                                "key": "conversation_summary",
                                "value": summary,
                                "type": "summary",
                            })
                            logger.info(f"Summarized conversation for user {user_id}")

        logger.info(f"Task completed: {task_type}")

    except Exception as e:
        logger.error(f"Task failed: {task_type} — {e}", exc_info=True)


async def main() -> None:
    """Worker main loop — listen for tasks on Redis queue."""
    logger.info("🚀 AION Worker starting...")

    redis_url = getattr(settings, "REDIS_URL", "redis://redis:6379/0")
    r = aioredis.from_url(redis_url, decode_responses=True)

    logger.info(f"Connected to Redis at {redis_url}")

    while True:
        try:
            # Blocking pop from task queue
            result = await r.blpop("aion:tasks", timeout=5)
            if result is None:
                continue

            _, task_data = result
            task = json.loads(task_data)
            await process_task(task)

        except asyncio.CancelledError:
            logger.info("Worker shutting down...")
            break
        except Exception as e:
            logger.error(f"Worker error: {e}", exc_info=True)
            await asyncio.sleep(1)

    await r.close()
    logger.info("Worker stopped")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [worker] %(levelname)s: %(message)s",
    )
    asyncio.run(main())
