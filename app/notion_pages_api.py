"""API для управления отдельными страницами Notion."""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import re
from .db import get_db
from .models import NotionPage
from .logger import get_logger
from .notion_sync import upsert_page
from notion_client import AsyncClient
from .config import settings

logger = get_logger(__name__)
router = APIRouter(prefix="/api")
notion = AsyncClient(auth=settings.notion_token)


class NotionPageCreate(BaseModel):
    page_url: str
    allowed_roles: list[str] = ["Recruiter", "Team Lead", "Head"]


def extract_page_id_from_url(url: str) -> str:
    """Extract Notion page ID from URL."""
    # Notion URLs format: https://www.notion.so/Page-Title-<page_id>
    # page_id is the last part with dashes, 32 characters (with dashes)
    match = re.search(r'([a-f0-9]{32}|[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})$', url.replace('-', ''))
    
    if match:
        page_id = match.group(1)
        # Format as UUID if needed
        if len(page_id) == 32:
            # Convert to UUID format
            return f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:]}"
        return page_id
    
    # Alternative: try to extract from URL directly
    # Format: https://www.notion.so/workspace/Page-Title-abc123def456
    parts = url.rstrip('/').split('/')
    if parts:
        last_part = parts[-1]
        # Remove query params
        last_part = last_part.split('?')[0]
        # Get ID part (last 32 characters without dashes)
        clean_id = last_part.replace('-', '')
        if len(clean_id) >= 32:
            page_id = clean_id[-32:]
            return f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:]}"
    
    raise ValueError("Could not extract page ID from URL")


@router.get("/notion-pages")
async def get_notion_pages(db: AsyncSession = Depends(get_db)):
    """Get all notion pages."""
    try:
        result = await db.execute(select(NotionPage).order_by(NotionPage.created_at.desc()))
        pages = result.scalars().all()
        
        return [
            {
                "id": page.id,
                "page_url": page.page_url,
                "page_id": page.page_id,
                "title": page.title,
                "allowed_roles": page.allowed_roles or [],
                "status": page.status,
                "last_synced": page.last_synced.isoformat() if page.last_synced else None,
                "error_message": page.error_message,
                "created_at": page.created_at.isoformat(),
                "updated_at": page.updated_at.isoformat(),
            }
            for page in pages
        ]
    except Exception as e:
        logger.error("Error fetching notion pages", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch notion pages")


@router.post("/notion-pages")
async def create_notion_page(data: NotionPageCreate, db: AsyncSession = Depends(get_db)):
    """Add new notion page."""
    try:
        # Extract page ID from URL
        try:
            page_id = extract_page_id_from_url(data.page_url)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid Notion URL: {str(e)}")
        
        # Check if page already exists
        result = await db.execute(select(NotionPage).where(NotionPage.page_id == page_id))
        existing_page = result.scalar_one_or_none()
        
        if existing_page:
            raise HTTPException(status_code=400, detail="Page already exists")
        
        # Try to get page title from Notion
        title = None
        try:
            page_data = await notion.pages.retrieve(page_id=page_id)
            title_prop = page_data["properties"].get("Name") or page_data["properties"].get("title")
            if title_prop:
                title = "".join([seg.get("plain_text", "") for seg in title_prop.get("title", [])]).strip()
        except Exception as e:
            logger.warning("Could not fetch page title", page_id=page_id, error=str(e))
        
        # Create new page
        page = NotionPage(
            page_url=data.page_url,
            page_id=page_id,
            title=title or "Untitled",
            allowed_roles=data.allowed_roles,
            status="pending",
        )
        db.add(page)
        await db.commit()
        await db.refresh(page)
        
        logger.info("Notion page created", page_id=page_id, title=title, roles=data.allowed_roles)
        
        return {
            "id": page.id,
            "page_url": page.page_url,
            "page_id": page.page_id,
            "title": page.title,
            "allowed_roles": page.allowed_roles,
            "status": page.status,
            "last_synced": None,
            "error_message": None,
            "created_at": page.created_at.isoformat(),
            "updated_at": page.updated_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating notion page", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create notion page")


@router.post("/notion-pages/{page_id}/sync")
async def sync_notion_page(page_id: int, db: AsyncSession = Depends(get_db)):
    """Sync specific notion page."""
    try:
        # Get page from DB
        result = await db.execute(select(NotionPage).where(NotionPage.id == page_id))
        page = result.scalar_one_or_none()
        
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
        
        # Update status to syncing
        page.status = "syncing"
        page.error_message = None
        await db.commit()
        
        try:
            # Get page metadata from Notion
            page_data = await notion.pages.retrieve(page_id=page.page_id)
            last_edited_str = page_data.get("last_edited_time")
            last_edited = datetime.fromisoformat(last_edited_str.replace("Z", "+00:00")) if last_edited_str else datetime.utcnow()
            
            # Update title if changed
            title_prop = page_data["properties"].get("Name") or page_data["properties"].get("title")
            if title_prop:
                new_title = "".join([seg.get("plain_text", "") for seg in title_prop.get("title", [])]).strip()
                if new_title:
                    page.title = new_title
            
            # Sync page content with allowed roles
            await upsert_page(db, page.page_id, last_edited, allowed_roles=page.allowed_roles)
            
            # Update status to synced
            page.status = "synced"
            page.last_synced = datetime.utcnow()
            await db.commit()
            await db.refresh(page)
            
            logger.info("Notion page synced successfully", page_id=page.page_id)
            
            return {
                "id": page.id,
                "page_url": page.page_url,
                "page_id": page.page_id,
                "title": page.title,
                "allowed_roles": page.allowed_roles,
                "status": page.status,
                "last_synced": page.last_synced.isoformat() if page.last_synced else None,
                "error_message": page.error_message,
                "created_at": page.created_at.isoformat(),
                "updated_at": page.updated_at.isoformat(),
            }
            
        except Exception as e:
            # Update status to error
            page.status = "error"
            page.error_message = str(e)
            await db.commit()
            logger.error("Error syncing notion page", page_id=page.page_id, error=str(e))
            raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in sync endpoint", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to sync page")


@router.delete("/notion-pages/{page_id}")
async def delete_notion_page(page_id: int, db: AsyncSession = Depends(get_db)):
    """Delete notion page from management (doesn't delete from documents)."""
    try:
        result = await db.execute(select(NotionPage).where(NotionPage.id == page_id))
        page = result.scalar_one_or_none()
        
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
        
        await db.delete(page)
        await db.commit()
        
        logger.info("Notion page deleted from management", page_id=page_id)
        return {"message": "Page deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting notion page", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete notion page")

