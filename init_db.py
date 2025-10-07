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
            # Check if pgvector is available
            pgvector_available = False
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                logger.info("pgvector extension enabled")
                pgvector_available = True
            except Exception as ext_error:
                logger.warning(
                    "Could not enable pgvector extension - will use TEXT for embeddings",
                    error=str(ext_error)
                )
            
            # Read and execute SQL migration file
            sql_file = os.path.join(os.path.dirname(__file__), "migrations", "001_init.sql")
            if os.path.exists(sql_file):
                with open(sql_file, 'r') as f:
                    sql_content = f.read()
                    
                # If pgvector not available, replace VECTOR type with TEXT
                if not pgvector_available:
                    sql_content = sql_content.replace("VECTOR(1536)", "TEXT")
                    sql_content = sql_content.replace(
                        'USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)',
                        ''
                    )
                    logger.info("Using TEXT type for embeddings (pgvector not available)")
                
                # Execute each statement separately
                for statement in sql_content.split(';'):
                    statement = statement.strip()
                    if statement and not statement.startswith('--'):
                        try:
                            await conn.execute(text(statement))
                        except Exception as stmt_error:
                            # Ignore "already exists" errors
                            if "already exists" not in str(stmt_error).lower():
                                logger.warning(f"Statement error: {stmt_error}")
                
                logger.info("Database tables created from migration file")
            else:
                # Fallback to SQLAlchemy metadata (might fail without pgvector)
                from app.models import Base
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created from models")
            
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        raise


if __name__ == "__main__":
    asyncio.run(init_database())
