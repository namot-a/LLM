#!/usr/bin/env python3
"""Sync Notion databases with the application."""
import asyncio
from app.db import get_db
from app.notion_sync import ingest_all
from app.logger import get_logger

logger = get_logger(__name__)


async def sync_notion():
    """Sync all Notion databases."""
    try:
        async for db in get_db():
            stats = await ingest_all(db)
            logger.info("Notion sync completed", stats=stats)
    except Exception as e:
        logger.error("Notion sync failed", error=str(e))
        raise


if __name__ == "__main__":
    asyncio.run(sync_notion())
