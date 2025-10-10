"""Apply database migration 002."""
import asyncio
from app.db import engine
from sqlalchemy import text
from app.logger import get_logger

logger = get_logger(__name__)


async def apply_migration():
    """Apply migration 002."""
    try:
        async with engine.begin() as conn:
            logger.info("Applying migration 002: Add role-based access control")
            
            # Read migration file
            with open("migrations/002_add_roles.sql", "r") as f:
                migration_sql = f.read()
            
            # Execute migration
            await conn.execute(text(migration_sql))
            
            logger.info("✓ Migration 002 applied successfully")
            
    except Exception as e:
        logger.error("✗ Migration failed", error=str(e))
        raise


if __name__ == "__main__":
    asyncio.run(apply_migration())

