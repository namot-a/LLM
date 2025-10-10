"""Admin endpoints for database management."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from .db import get_db, engine
from .config import settings
from .logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/admin")


@router.post("/apply-migration-002")
async def apply_migration_002(secret: str):
    """Apply migration 002 to add role-based access control columns."""
    if secret != settings.webhook_secret_path:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    try:
        async with engine.begin() as conn:
            logger.info("Applying migration 002")
            
            # Add allowed_roles to documents
            await conn.execute(text(
                "ALTER TABLE documents ADD COLUMN IF NOT EXISTS allowed_roles TEXT[]"
            ))
            
            # Add allowed_roles to chunks
            await conn.execute(text(
                "ALTER TABLE chunks ADD COLUMN IF NOT EXISTS allowed_roles TEXT[]"
            ))
            
            # Add allowed_roles to notion_pages
            await conn.execute(text(
                "ALTER TABLE notion_pages ADD COLUMN IF NOT EXISTS allowed_roles TEXT[] DEFAULT ARRAY['Recruiter', 'Team Lead', 'Head']"
            ))
            
            # Add has_answer to query_logs
            await conn.execute(text(
                "ALTER TABLE query_logs ADD COLUMN IF NOT EXISTS has_answer BOOLEAN DEFAULT TRUE"
            ))
            
            # Create indexes
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_documents_allowed_roles ON documents USING GIN (allowed_roles)"
            ))
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_chunks_allowed_roles ON chunks USING GIN (allowed_roles)"
            ))
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_query_logs_has_answer ON query_logs(has_answer)"
            ))
            
            # Set default roles for existing records
            await conn.execute(text(
                "UPDATE notion_pages SET allowed_roles = ARRAY['Recruiter', 'Team Lead', 'Head'] WHERE allowed_roles IS NULL"
            ))
            await conn.execute(text(
                "UPDATE documents SET allowed_roles = ARRAY['Recruiter', 'Team Lead', 'Head'] WHERE allowed_roles IS NULL"
            ))
            
            # Mark all existing queries as having answers (legacy data)
            await conn.execute(text(
                "UPDATE query_logs SET has_answer = TRUE WHERE has_answer IS NULL"
            ))
            
            logger.info("✓ Migration 002 applied successfully")
            
        return {
            "status": "ok",
            "message": "Migration 002 applied successfully",
            "changes": [
                "Added allowed_roles to documents table",
                "Added allowed_roles to chunks table",
                "Added allowed_roles to notion_pages table",
                "Added has_answer to query_logs table",
                "Created GIN indexes for role filtering",
                "Set default roles for existing records"
            ]
        }
    except Exception as e:
        logger.error("Migration 002 failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")

