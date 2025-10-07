#!/usr/bin/env python3
"""Initialize database with tables and extensions."""
import asyncio
import os
from sqlalchemy import text
from app.db import engine
from app.logger import get_logger

logger = get_logger(__name__)


async def init_database():
    """Initialize database with required extensions and tables."""
    try:
        async with engine.begin() as conn:
            # Enable pgvector extension
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            logger.info("pgvector extension enabled")
            
            # Create tables using SQLAlchemy metadata
            from app.models import Base
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")
            
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        raise


if __name__ == "__main__":
    asyncio.run(init_database())
