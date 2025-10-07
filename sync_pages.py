#!/usr/bin/env python3
"""Sync individual Notion pages with the application."""
import asyncio
from app.db import get_db
from app.notion_sync import upsert_page
from app.logger import get_logger
from app.config import settings
from datetime import datetime

logger = get_logger(__name__)


async def sync_pages():
    """Sync individual Notion pages."""
    try:
        # Get page IDs from settings
        page_ids = settings.get_database_ids()  # These are actually page IDs
        
        logger.info("Starting page sync", pages=page_ids)
        
        async for db in get_db():
            stats = {"processed": 0, "errors": 0, "pages": len(page_ids)}
            
            for page_id in page_ids:
                try:
                    logger.info("Processing page", page_id=page_id)
                    
                    # Get current timestamp for last_edited
                    last_edited = datetime.utcnow()
                    
                    # Upsert the page
                    await upsert_page(db, page_id, last_edited)
                    
                    stats["processed"] += 1
                    logger.info("Page processed successfully", page_id=page_id)
                    
                except Exception as e:
                    logger.error("Error processing page", page_id=page_id, error=str(e))
                    stats["errors"] += 1
                    continue
            
            logger.info("Page sync completed", stats=stats)
            
    except Exception as e:
        logger.error("Page sync failed", error=str(e))
        raise


if __name__ == "__main__":
    asyncio.run(sync_pages())
