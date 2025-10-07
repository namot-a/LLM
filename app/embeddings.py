"""Embeddings service with error handling and retry logic."""
import asyncio
from typing import List, Optional
from openai import AsyncOpenAI, RateLimitError, APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .config import settings
from .logger import get_logger
from .exceptions import OpenAIError

logger = get_logger(__name__)

client = AsyncOpenAI(api_key=settings.openai_api_key)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((RateLimitError, APIError)),
    reraise=True
)
async def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Create embeddings for a list of texts with retry logic.
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors
        
    Raises:
        OpenAIError: If embedding creation fails
    """
    if not texts:
        return []
    
    try:
        logger.info("Creating embeddings", count=len(texts), model=settings.openai_embed_model)
        
        # OpenAI has limits on batch size, so we chunk if necessary
        max_batch_size = 100  # Conservative limit
        all_embeddings = []
        
        for i in range(0, len(texts), max_batch_size):
            batch = texts[i:i + max_batch_size]
            response = await client.embeddings.create(
                model=settings.openai_embed_model,
                input=batch
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
            
            # Small delay between batches to be respectful
            if i + max_batch_size < len(texts):
                await asyncio.sleep(0.1)
        
        logger.info("Embeddings created successfully", count=len(all_embeddings))
        return all_embeddings
        
    except RateLimitError as e:
        logger.error("Rate limit exceeded for embeddings", error=str(e))
        raise OpenAIError(f"Rate limit exceeded: {e}", "rate_limit")
    except APIError as e:
        logger.error("OpenAI API error for embeddings", error=str(e), status_code=getattr(e, 'status_code', None))
        raise OpenAIError(f"OpenAI API error: {e}", "api_error")
    except Exception as e:
        logger.error("Unexpected error creating embeddings", error=str(e))
        raise OpenAIError(f"Unexpected error: {e}", "unknown")


async def embed_query(text: str) -> List[float]:
    """
    Create embedding for a single query text.
    
    Args:
        text: Query text to embed
        
    Returns:
        Embedding vector
        
    Raises:
        OpenAIError: If embedding creation fails
    """
    if not text.strip():
        raise ValueError("Query text cannot be empty")
    
    embeddings = await embed_texts([text])
    return embeddings[0]


async def embed_text_batch(texts: List[str], batch_size: int = 50) -> List[List[float]]:
    """
    Create embeddings for texts in batches with progress tracking.
    
    Args:
        texts: List of texts to embed
        batch_size: Size of each batch
        
    Returns:
        List of embedding vectors
    """
    if not texts:
        return []
    
    all_embeddings = []
    total_batches = (len(texts) + batch_size - 1) // batch_size
    
    logger.info("Starting batch embedding", total_texts=len(texts), batch_size=batch_size, total_batches=total_batches)
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_num = i // batch_size + 1
        
        logger.info("Processing batch", batch_num=batch_num, total_batches=total_batches, batch_size=len(batch))
        
        try:
            batch_embeddings = await embed_texts(batch)
            all_embeddings.extend(batch_embeddings)
        except Exception as e:
            logger.error("Failed to process batch", batch_num=batch_num, error=str(e))
            # Continue with other batches instead of failing completely
            continue
    
    logger.info("Batch embedding completed", total_embeddings=len(all_embeddings), expected=len(texts))
    return all_embeddings
