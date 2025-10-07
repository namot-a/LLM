"""FastAPI routes with improved error handling and validation."""
import time
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from .db import get_db
from .config import settings
from .logger import get_logger
from .exceptions import NotionRAGError, NotionAPIError, OpenAIError, RetrievalError
from .notion_sync import ingest_all
from .retrieval import retrieve, format_sources
from .llm import answer_with_context, calculate_cost
from .models import QueryLog, Feedback

logger = get_logger(__name__)
router = APIRouter()


# Pydantic models for request/response validation
class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="User question")
    telegram_user_id: Optional[int] = Field(None, description="Telegram user ID")
    include_sources: bool = Field(True, description="Include source references")


class QueryResponse(BaseModel):
    answer: str = Field(..., description="Generated answer")
    sources: Optional[list] = Field(None, description="Source references")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    tokens_used: Optional[int] = Field(None, description="Total tokens used")


class FeedbackRequest(BaseModel):
    message_id: Optional[int] = Field(None, description="Telegram message ID")
    rating: str = Field(..., pattern="^(good|bad)$", description="Feedback rating")
    comment: Optional[str] = Field(None, max_length=500, description="Optional comment")


class IngestResponse(BaseModel):
    status: str = Field(..., description="Ingestion status")
    stats: Dict[str, int] = Field(..., description="Ingestion statistics")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@router.post("/admin/ingest", response_model=IngestResponse)
async def admin_ingest(secret: str, background_tasks: BackgroundTasks):
    """Trigger Notion database ingestion."""
    if secret != settings.webhook_secret_path:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    try:
        logger.info("Starting Notion ingestion")
        async with get_db() as db:
            stats = await ingest_all(db)
        
        return IngestResponse(
            status="completed",
            stats=stats
        )
    except Exception as e:
        logger.error("Ingestion failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest, db: AsyncSession = Depends(get_db)):
    """Process user query and return answer."""
    start_time = time.time()
    
    try:
        logger.info("Processing query", 
                   question=request.question[:100], 
                   user_id=request.telegram_user_id)
        
        # Get database session
        # Retrieve relevant chunks
        chunks = await retrieve(db, request.question)
        
        if not chunks:
            logger.warning("No relevant chunks found", question=request.question[:100])
            return QueryResponse(
                answer="Я не нашла релевантной информации в регламентах. Попробуйте переформулировать вопрос или обратитесь к администратору.",
                sources=[] if request.include_sources else None,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Generate answer using LLM
        llm_response = await answer_with_context(request.question, chunks)
        
        # Format sources if requested
        sources = None
        if request.include_sources:
            sources = format_sources(chunks)
        
        # Calculate cost
        cost = calculate_cost(
            llm_response.get("prompt_tokens", 0),
            llm_response.get("completion_tokens", 0)
        )
        
        # Log query
        processing_time = int((time.time() - start_time) * 1000)
        query_log = QueryLog(
            ts=datetime.utcnow(),
            telegram_user_id=request.telegram_user_id,
            question=request.question,
            answer=llm_response["answer"],
            prompt_tokens=llm_response.get("prompt_tokens"),
            completion_tokens=llm_response.get("completion_tokens"),
            model=llm_response.get("model"),
            cost_usd=cost,
            processing_time_ms=processing_time
        )
        db.add(query_log)
        
        logger.info("Query processed successfully", 
                   user_id=request.telegram_user_id,
                   tokens_used=llm_response.get("total_tokens", 0),
                   processing_time_ms=processing_time)
        
        return QueryResponse(
            answer=llm_response["answer"],
            sources=sources,
            processing_time_ms=processing_time,
            tokens_used=llm_response.get("total_tokens")
        )
        
    except RetrievalError as e:
        logger.error("Retrieval error", error=str(e))
        raise HTTPException(status_code=500, detail="Document retrieval failed")
    except OpenAIError as e:
        logger.error("OpenAI error", error=str(e))
        raise HTTPException(status_code=500, detail="AI service temporarily unavailable")
    except NotionAPIError as e:
        logger.error("Notion API error", error=str(e))
        raise HTTPException(status_code=500, detail="Document service temporarily unavailable")
    except Exception as e:
        logger.error("Unexpected error in query", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    telegram_user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Submit user feedback."""
    try:
        feedback = Feedback(
            telegram_user_id=telegram_user_id,
            message_id=request.message_id,
            rating=request.rating,
            comment=request.comment
        )
        db.add(feedback)
        
        logger.info("Feedback submitted", 
                   user_id=telegram_user_id, 
                   rating=request.rating)
        
        return {"status": "success", "message": "Feedback received"}
        
    except Exception as e:
        logger.error("Error submitting feedback", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get basic statistics (admin only)."""
    # This would require additional implementation
    return {"message": "Stats endpoint not implemented yet"}


# Exception handlers are handled in individual endpoints
