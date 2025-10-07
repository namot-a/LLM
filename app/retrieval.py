"""Document retrieval with vector similarity search."""
from typing import List, Dict, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import os
from .config import settings
from .logger import get_logger
from .exceptions import RetrievalError
from .embeddings import embed_query

logger = get_logger(__name__)


async def retrieve(db: AsyncSession, question: str) -> List[Dict]:
    """
    Retrieve relevant document chunks using vector similarity search.
    
    Args:
        db: Database session
        question: User question
        
    Returns:
        List of relevant chunks with metadata
        
    Raises:
        RetrievalError: If retrieval fails
    """
    try:
        logger.info("Starting retrieval", question=question[:100])
        
        # Create query embedding
        query_embedding = await embed_query(question)
        
        # Vector similarity search using pgvector
        sql = text("""
            SELECT 
                c.id,
                c.content,
                c.heading_path,
                d.title,
                d.url,
                d.last_edited,
                1 - (c.embedding <=> :query_embedding)::float as cosine_similarity
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY c.embedding <-> :query_embedding
            LIMIT :top_k
        """)
        
        # Convert embedding list to string format for pgvector
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        result = await db.execute(sql, {
            "query_embedding": embedding_str,
            "top_k": settings.top_k
        })
        
        rows = result.mappings().all()
        chunks = [dict(row) for row in rows]
        
        # Filter by similarity threshold
        filtered_chunks = [
            chunk for chunk in chunks 
            if chunk["cosine_similarity"] >= (1 - settings.similarity_threshold)
        ]
        
        # If no chunks meet threshold, return top results anyway
        if not filtered_chunks and chunks:
            filtered_chunks = chunks[:3]  # Return top 3 if no good matches
            logger.warning("No chunks met similarity threshold, returning top results", 
                         threshold=settings.similarity_threshold, returned=len(filtered_chunks))
        
        logger.info("Retrieval completed", 
                   total_found=len(chunks), 
                   filtered=len(filtered_chunks),
                   threshold=settings.similarity_threshold)
        
        return filtered_chunks
        
    except Exception as e:
        logger.error("Retrieval failed", question=question[:100], error=str(e))
        raise RetrievalError(f"Failed to retrieve documents: {e}")


async def retrieve_with_filters(
    db: AsyncSession, 
    question: str, 
    document_ids: Optional[List[str]] = None,
    min_similarity: Optional[float] = None
) -> List[Dict]:
    """
    Retrieve documents with additional filters.
    
    Args:
        db: Database session
        question: User question
        document_ids: Optional list of document IDs to filter by
        min_similarity: Optional minimum similarity threshold
        
    Returns:
        List of relevant chunks with metadata
    """
    try:
        logger.info("Starting filtered retrieval", 
                   question=question[:100], 
                   document_ids=document_ids,
                   min_similarity=min_similarity)
        
        query_embedding = await embed_query(question)
        
        # Convert embedding list to string format for pgvector
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        # Build dynamic SQL with filters
        where_conditions = []
        params = {
            "query_embedding": embedding_str,
            "top_k": settings.top_k
        }
        
        if document_ids:
            where_conditions.append("d.id = ANY(:document_ids)")
            params["document_ids"] = document_ids
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        sql = text(f"""
            SELECT 
                c.id,
                c.content,
                c.heading_path,
                d.title,
                d.url,
                d.last_edited,
                1 - (c.embedding <=> :query_embedding)::float as cosine_similarity
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            {where_clause}
            ORDER BY c.embedding <-> :query_embedding
            LIMIT :top_k
        """)
        
        result = await db.execute(sql, params)
        rows = result.mappings().all()
        chunks = [dict(row) for row in rows]
        
        # Apply similarity threshold
        threshold = min_similarity or (1 - settings.similarity_threshold)
        filtered_chunks = [
            chunk for chunk in chunks 
            if chunk["cosine_similarity"] >= threshold
        ]
        
        logger.info("Filtered retrieval completed", 
                   total_found=len(chunks), 
                   filtered=len(filtered_chunks))
        
        return filtered_chunks
        
    except Exception as e:
        logger.error("Filtered retrieval failed", question=question[:100], error=str(e))
        raise RetrievalError(f"Failed to retrieve documents with filters: {e}")


def format_sources(chunks: List[Dict], max_sources: int = 3) -> List[Dict]:
    """
    Format chunks into source references.
    
    Args:
        chunks: List of chunk dictionaries
        max_sources: Maximum number of sources to return
        
    Returns:
        List of formatted source dictionaries
    """
    sources = []
    seen = set()
    
    for chunk in chunks[:max_sources]:
        # Create unique key for deduplication
        key = (chunk["title"], chunk["url"], chunk.get("heading_path", ""))
        
        if key not in seen:
            seen.add(key)
            sources.append({
                "title": chunk["title"],
                "url": chunk["url"],
                "section": chunk.get("heading_path", ""),
                "similarity": chunk.get("cosine_similarity", 0)
            })
    
    return sources
