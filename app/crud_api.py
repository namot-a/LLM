"""CRUD API endpoints for admin panel."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from .db import get_db
from .models import Document, Chunk, QueryLog, Feedback, TelegramUser
from .logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api")


# Pydantic models for responses
class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    allowed_roles: Optional[list[str]] = None


class ChunkUpdate(BaseModel):
    content: Optional[str] = None
    heading_path: Optional[str] = None


class TelegramUserCreate(BaseModel):
    user_id: int
    username: Optional[str] = None
    role: str = "Recruiter"  # Recruiter, Team Lead, Head


class TelegramUserUpdate(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


# Documents endpoints
@router.get("/documents")
async def get_documents(db: AsyncSession = Depends(get_db)):
    """Get all documents."""
    try:
        result = await db.execute(select(Document).order_by(Document.last_edited.desc()))
        documents = result.scalars().all()
        
        return [
            {
                "id": str(doc.id),
                "notion_page_id": doc.notion_page_id,
                "title": doc.title,
                "url": doc.url,
                "allowed_roles": doc.allowed_roles or [],
                "last_edited": doc.last_edited.isoformat(),
                "created_at": doc.created_at.isoformat(),
                "updated_at": doc.updated_at.isoformat(),
            }
            for doc in documents
        ]
    except Exception as e:
        logger.error("Error fetching documents", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch documents")


@router.get("/documents/{document_id}")
async def get_document(document_id: str, db: AsyncSession = Depends(get_db)):
    """Get document by ID."""
    try:
        result = await db.execute(select(Document).where(Document.id == document_id))
        doc = result.scalar_one_or_none()
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "id": str(doc.id),
            "notion_page_id": doc.notion_page_id,
            "title": doc.title,
            "url": doc.url,
            "allowed_roles": doc.allowed_roles or [],
            "last_edited": doc.last_edited.isoformat(),
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.updated_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching document", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch document")


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db)):
    """Delete document and its chunks."""
    try:
        result = await db.execute(select(Document).where(Document.id == document_id))
        doc = result.scalar_one_or_none()
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        await db.delete(doc)
        
        logger.info("Document deleted", document_id=document_id)
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting document", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete document")


@router.put("/documents/{document_id}")
async def update_document(
    document_id: str, 
    data: DocumentUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update document."""
    try:
        result = await db.execute(select(Document).where(Document.id == document_id))
        doc = result.scalar_one_or_none()
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if data.title is not None:
            doc.title = data.title
        if data.url is not None:
            doc.url = data.url
        if data.allowed_roles is not None:
            doc.allowed_roles = data.allowed_roles
            # Also update all chunks of this document
            from sqlalchemy import update
            await db.execute(
                update(Chunk)
                .where(Chunk.document_id == doc.id)
                .values(allowed_roles=data.allowed_roles)
            )
        
        await db.commit()
        await db.refresh(doc)
        
        logger.info("Document updated", document_id=document_id, allowed_roles=data.allowed_roles)
        
        return {
            "id": str(doc.id),
            "notion_page_id": doc.notion_page_id,
            "title": doc.title,
            "url": doc.url,
            "allowed_roles": doc.allowed_roles or [],
            "last_edited": doc.last_edited.isoformat(),
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.updated_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating document", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update document")


# Chunks endpoints
@router.get("/chunks")
async def get_chunks(limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all chunks (limited)."""
    try:
        result = await db.execute(
            select(Chunk).order_by(Chunk.created_at.desc()).limit(limit)
        )
        chunks = result.scalars().all()
        
        return [
            {
                "id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "chunk_index": chunk.chunk_index,
                "heading_path": chunk.heading_path,
                "content": chunk.content,
                "created_at": chunk.created_at.isoformat(),
            }
            for chunk in chunks
        ]
    except Exception as e:
        logger.error("Error fetching chunks", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch chunks")


@router.get("/chunks/document/{document_id}")
async def get_chunks_by_document(document_id: str, db: AsyncSession = Depends(get_db)):
    """Get all chunks for a document."""
    try:
        result = await db.execute(
            select(Chunk)
            .where(Chunk.document_id == document_id)
            .order_by(Chunk.chunk_index)
        )
        chunks = result.scalars().all()
        
        return [
            {
                "id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "chunk_index": chunk.chunk_index,
                "heading_path": chunk.heading_path,
                "content": chunk.content,
                "created_at": chunk.created_at.isoformat(),
            }
            for chunk in chunks
        ]
    except Exception as e:
        logger.error("Error fetching chunks", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch chunks")


@router.get("/chunks/{chunk_id}")
async def get_chunk(chunk_id: str, db: AsyncSession = Depends(get_db)):
    """Get chunk by ID."""
    try:
        result = await db.execute(select(Chunk).where(Chunk.id == chunk_id))
        chunk = result.scalar_one_or_none()
        
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        
        return {
            "id": str(chunk.id),
            "document_id": str(chunk.document_id),
            "chunk_index": chunk.chunk_index,
            "heading_path": chunk.heading_path,
            "content": chunk.content,
            "created_at": chunk.created_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching chunk", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch chunk")


@router.delete("/chunks/{chunk_id}")
async def delete_chunk(chunk_id: str, db: AsyncSession = Depends(get_db)):
    """Delete chunk."""
    try:
        result = await db.execute(select(Chunk).where(Chunk.id == chunk_id))
        chunk = result.scalar_one_or_none()
        
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        
        await db.delete(chunk)
        
        logger.info("Chunk deleted", chunk_id=chunk_id)
        return {"message": "Chunk deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting chunk", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete chunk")


@router.put("/chunks/{chunk_id}")
async def update_chunk(
    chunk_id: str, 
    data: ChunkUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update chunk."""
    try:
        result = await db.execute(select(Chunk).where(Chunk.id == chunk_id))
        chunk = result.scalar_one_or_none()
        
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        
        if data.content is not None:
            chunk.content = data.content
        if data.heading_path is not None:
            chunk.heading_path = data.heading_path
        
        logger.info("Chunk updated", chunk_id=chunk_id)
        
        return {
            "id": str(chunk.id),
            "document_id": str(chunk.document_id),
            "chunk_index": chunk.chunk_index,
            "heading_path": chunk.heading_path,
            "content": chunk.content,
            "created_at": chunk.created_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating chunk", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update chunk")


# Query logs endpoints
@router.get("/query-logs")
async def get_query_logs(limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """Get all query logs."""
    try:
        query = select(QueryLog).order_by(QueryLog.ts.desc())
        if limit:
            query = query.limit(limit)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return [
            {
                "id": log.id,
                "ts": log.ts.isoformat(),
                "telegram_user_id": log.telegram_user_id,
                "question": log.question,
                "answer": log.answer,
                "prompt_tokens": log.prompt_tokens,
                "completion_tokens": log.completion_tokens,
                "model": log.model,
                "cost_usd": str(log.cost_usd) if log.cost_usd else None,
                "processing_time_ms": log.processing_time_ms,
            }
            for log in logs
        ]
    except Exception as e:
        logger.error("Error fetching query logs", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch query logs")


@router.get("/query-logs/{log_id}")
async def get_query_log(log_id: int, db: AsyncSession = Depends(get_db)):
    """Get query log by ID."""
    try:
        result = await db.execute(select(QueryLog).where(QueryLog.id == log_id))
        log = result.scalar_one_or_none()
        
        if not log:
            raise HTTPException(status_code=404, detail="Query log not found")
        
        return {
            "id": log.id,
            "ts": log.ts.isoformat(),
            "telegram_user_id": log.telegram_user_id,
            "question": log.question,
            "answer": log.answer,
            "prompt_tokens": log.prompt_tokens,
            "completion_tokens": log.completion_tokens,
            "model": log.model,
            "cost_usd": str(log.cost_usd) if log.cost_usd else None,
            "processing_time_ms": log.processing_time_ms,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching query log", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch query log")


@router.delete("/query-logs/{log_id}")
async def delete_query_log(log_id: int, db: AsyncSession = Depends(get_db)):
    """Delete query log."""
    try:
        result = await db.execute(select(QueryLog).where(QueryLog.id == log_id))
        log = result.scalar_one_or_none()
        
        if not log:
            raise HTTPException(status_code=404, detail="Query log not found")
        
        await db.delete(log)
        
        logger.info("Query log deleted", log_id=log_id)
        return {"message": "Query log deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting query log", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete query log")


# Feedback endpoints
@router.get("/feedback")
async def get_feedback(limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """Get all feedback."""
    try:
        query = select(Feedback).order_by(Feedback.ts.desc())
        if limit:
            query = query.limit(limit)
        
        result = await db.execute(query)
        feedback_list = result.scalars().all()
        
        return [
            {
                "id": fb.id,
                "ts": fb.ts.isoformat(),
                "telegram_user_id": fb.telegram_user_id,
                "message_id": fb.message_id,
                "query_log_id": fb.query_log_id,
                "rating": fb.rating,
                "comment": fb.comment,
            }
            for fb in feedback_list
        ]
    except Exception as e:
        logger.error("Error fetching feedback", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch feedback")


@router.get("/feedback/{feedback_id}")
async def get_feedback_by_id(feedback_id: int, db: AsyncSession = Depends(get_db)):
    """Get feedback by ID."""
    try:
        result = await db.execute(select(Feedback).where(Feedback.id == feedback_id))
        fb = result.scalar_one_or_none()
        
        if not fb:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        return {
            "id": fb.id,
            "ts": fb.ts.isoformat(),
            "telegram_user_id": fb.telegram_user_id,
            "message_id": fb.message_id,
            "query_log_id": fb.query_log_id,
            "rating": fb.rating,
            "comment": fb.comment,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching feedback", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch feedback")


@router.delete("/feedback/{feedback_id}")
async def delete_feedback(feedback_id: int, db: AsyncSession = Depends(get_db)):
    """Delete feedback."""
    try:
        result = await db.execute(select(Feedback).where(Feedback.id == feedback_id))
        fb = result.scalar_one_or_none()
        
        if not fb:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        await db.delete(fb)
        
        logger.info("Feedback deleted", feedback_id=feedback_id)
        return {"message": "Feedback deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting feedback", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete feedback")


# Telegram Users endpoints
@router.get("/telegram-users")
async def get_telegram_users(db: AsyncSession = Depends(get_db)):
    """Get all telegram users."""
    try:
        result = await db.execute(select(TelegramUser).order_by(TelegramUser.created_at.desc()))
        users = result.scalars().all()
        
        return [
            {
                "user_id": user.user_id,
                "username": user.username,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            }
            for user in users
        ]
    except Exception as e:
        logger.error("Error fetching telegram users", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch telegram users")


@router.get("/telegram-users/{user_id}")
async def get_telegram_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get telegram user by ID."""
    try:
        result = await db.execute(select(TelegramUser).where(TelegramUser.user_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching telegram user", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch telegram user")


@router.post("/telegram-users")
async def create_telegram_user(data: TelegramUserCreate, db: AsyncSession = Depends(get_db)):
    """Create telegram user."""
    try:
        # Check if user already exists
        result = await db.execute(select(TelegramUser).where(TelegramUser.user_id == data.user_id))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        user = TelegramUser(
            user_id=data.user_id,
            username=data.username,
            role=data.role,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info("Telegram user created", user_id=data.user_id)
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating telegram user", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create telegram user")


@router.put("/telegram-users/{user_id}")
async def update_telegram_user(
    user_id: int, 
    data: TelegramUserUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update telegram user."""
    try:
        result = await db.execute(select(TelegramUser).where(TelegramUser.user_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if data.username is not None:
            user.username = data.username
        if data.role is not None:
            user.role = data.role
        if data.is_active is not None:
            user.is_active = data.is_active
        
        await db.commit()
        await db.refresh(user)
        
        logger.info("Telegram user updated", user_id=user_id)
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating telegram user", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update telegram user")


@router.delete("/telegram-users/{user_id}")
async def delete_telegram_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Delete telegram user."""
    try:
        result = await db.execute(select(TelegramUser).where(TelegramUser.user_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        await db.delete(user)
        await db.commit()
        
        logger.info("Telegram user deleted", user_id=user_id)
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting telegram user", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete telegram user")

