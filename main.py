"""Main application entry point with proper lifecycle management."""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.logger import get_logger
from app.db import init_db, close_db
from app.api import router as api_router
from bot.telegram import router as telegram_router, set_webhook, delete_webhook

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Notion RAG Bot")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Set Telegram webhook
        await set_webhook()
        logger.info("Telegram webhook configured")
        
        yield
        
    except Exception as e:
        logger.error("Startup failed", error=str(e))
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Notion RAG Bot")
        
        try:
            # Delete webhook
            await delete_webhook()
            logger.info("Telegram webhook removed")
            
            # Close database connections
            await close_db()
            logger.info("Database connections closed")
            
        except Exception as e:
            logger.error("Shutdown error", error=str(e))


# Create FastAPI application
app = FastAPI(
    title="Notion RAG Bot",
    description="Telegram bot that answers questions based on Notion documentation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(telegram_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "notion-rag-bot",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes/container orchestration."""
    return {"status": "ready"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.log_level == "DEBUG",
        log_level=settings.log_level.lower()
    )
