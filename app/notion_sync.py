"""Notion synchronization with improved error handling and chunking."""
import asyncio
from datetime import datetime
from typing import List, Tuple, Dict, Optional
from notion_client import AsyncClient
from notion_client.errors import APIResponseError, RequestTimeoutError
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
import os
from .config import settings
from .logger import get_logger
from .exceptions import NotionAPIError
from .models import Document, Chunk
from .embeddings import embed_text_batch

logger = get_logger(__name__)

notion = AsyncClient(auth=settings.notion_token)

# Parse database IDs from settings
DATABASE_IDS = settings.get_database_ids()


def rich_text_to_plain(rt: List[dict]) -> str:
    """Convert Notion rich text to plain text."""
    if not rt:
        return ""
    return "".join([seg.get("plain_text", "") for seg in rt]).strip()


async def extract_page_text(page_id: str) -> Tuple[str, str, List[Tuple[str, str]]]:
    """
    Extract text content from a Notion page.
    
    Returns:
        Tuple of (title, url, [(heading_path, chunk_text), ...])
    """
    try:
        logger.info("Extracting page content", page_id=page_id)
        
        # Get page metadata
        page = await notion.pages.retrieve(page_id=page_id)
        title_prop = page["properties"].get("Name") or page["properties"].get("title")
        title = rich_text_to_plain(title_prop.get("title", [])) if title_prop else "Untitled"
        url = page.get("url", "")
        
        # Extract blocks content
        blocks = await notion.blocks.children.list(block_id=page_id)
        texts: List[Tuple[str, str]] = []  # (heading_path, text)
        heading_stack: List[str] = []
        
        def flush_paragraph(buf: List[str], path: str):
            """Flush accumulated paragraph text."""
            chunk = "\n".join([x for x in buf if x])
            if chunk.strip():
                texts.append((path, chunk.strip()))
        
        async def walk_blocks(block_id: str, heading_path: List[str]):
            """Recursively walk through blocks."""
            try:
                results = await notion.blocks.children.list(block_id=block_id)
                results = results.get("results", [])
                para_buf: List[str] = []
                
                for block in results:
                    block_type = block.get("type")
                    
                    if block_type in ("heading_1", "heading_2", "heading_3"):
                        # Flush accumulated paragraph
                        flush_paragraph(para_buf, " > ".join(heading_path))
                        para_buf.clear()
                        
                        # Extract heading text
                        txt = rich_text_to_plain(block[block_type].get("rich_text", []))
                        if not txt:
                            continue
                            
                        # Update heading path based on level
                        if block_type == "heading_1":
                            new_path = [txt]
                        elif block_type == "heading_2":
                            new_path = heading_path[:1] + [txt]
                        else:  # heading_3
                            new_path = heading_path[:2] + [txt]
                        
                        heading_path = new_path
                        
                    elif block_type in ("paragraph", "bulleted_list_item", "numbered_list_item", "quote", "callout"):
                        # Accumulate paragraph text
                        txt = rich_text_to_plain(block[block_type].get("rich_text", []))
                        if txt:
                            para_buf.append(txt)
                    
                    # Recursively process children
                    if block.get("has_children"):
                        await walk_blocks(block["id"], heading_path)
                
                # Flush remaining paragraph
                flush_paragraph(para_buf, " > ".join(heading_path))
                
            except Exception as e:
                logger.warning("Error processing blocks", block_id=block_id, error=str(e))
        
        await walk_blocks(page_id, [])
        
        # Chunk the extracted text
        chunks_with_path = []
        for path, paragraph in texts:
            for chunk in chunk_text(paragraph):
                chunks_with_path.append((path, chunk))
        
        logger.info("Page content extracted", page_id=page_id, title=title, chunks=len(chunks_with_path))
        return title, url, chunks_with_path
        
    except APIResponseError as e:
        logger.error("Notion API error", page_id=page_id, error=str(e), status_code=e.status)
        raise NotionAPIError(f"Notion API error: {e}", e.status)
    except RequestTimeoutError as e:
        logger.error("Notion request timeout", page_id=page_id, error=str(e))
        raise NotionAPIError(f"Notion request timeout: {e}")
    except Exception as e:
        logger.error("Unexpected error extracting page", page_id=page_id, error=str(e))
        raise NotionAPIError(f"Unexpected error: {e}")


def chunk_text(text: str, size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        size: Maximum chunk size
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if len(text) <= size:
        return [text] if text.strip() else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings within the last 100 characters
            search_start = max(start + size - 100, start)
            for i in range(end - 1, search_start - 1, -1):
                if text[i] in '.!?':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start < 0:
            start = 0
    
    return chunks


async def upsert_page(db: AsyncSession, page_id: str, last_edited: datetime) -> None:
    """Update or create a document and its chunks."""
    try:
        logger.info("Upserting page", page_id=page_id)
        
        # Check if document exists
        result = await db.execute(select(Document).where(Document.notion_page_id == page_id))
        doc = result.scalar_one_or_none()
        
        # Extract page content
        title, url, chunks_with_path = await extract_page_text(page_id)
        
        if doc is None:
            # Create new document
            doc = Document(
                notion_page_id=page_id,
                title=title,
                url=url,
                last_edited=last_edited
            )
            db.add(doc)
            await db.flush()
            logger.info("Created new document", document_id=doc.id, title=title)
        else:
            # Update existing document
            doc.title = title
            doc.url = url
            doc.last_edited = last_edited
            doc.updated_at = datetime.utcnow()
            
            # Remove old chunks
            await db.execute(delete(Chunk).where(Chunk.document_id == doc.id))
            await db.flush()
            logger.info("Updated document", document_id=doc.id, title=title)
        
        # Process chunks in batches
        if chunks_with_path:
            contents = [content for _, content in chunks_with_path]
            embeddings = await embed_text_batch(contents, batch_size=20)
            
            # Create chunk records
            for idx, ((path, content), embedding) in enumerate(zip(chunks_with_path, embeddings)):
                chunk = Chunk(
                    document_id=doc.id,
                    chunk_index=idx,
                    heading_path=path,
                    content=content,
                    embedding=embedding
                )
                db.add(chunk)
            
            await db.flush()
            logger.info("Created chunks", document_id=doc.id, count=len(chunks_with_path))
        
    except Exception as e:
        logger.error("Error upserting page", page_id=page_id, error=str(e))
        raise


async def ingest_all(db: AsyncSession) -> Dict[str, int]:
    """
    Ingest all pages from configured Notion page IDs.
    
    Returns:
        Dictionary with ingestion statistics
    """
    stats = {"processed": 0, "errors": 0, "pages": len(DATABASE_IDS)}
    
    logger.info("Starting Notion pages ingestion", pages=len(DATABASE_IDS))
    
    # Process each page ID directly (not as database)
    semaphore = asyncio.Semaphore(5)  # Limit concurrent requests
    
    async def process_single_page(page_id: str):
        """Process a single Notion page."""
        async with semaphore:
            try:
                logger.info("Processing page", page_id=page_id)
                
                # Get page metadata to retrieve last_edited_time
                page_data = await notion.pages.retrieve(page_id=page_id)
                last_edited_str = page_data.get("last_edited_time")
                
                if not last_edited_str:
                    logger.warning("No last_edited_time for page", page_id=page_id)
                    last_edited = datetime.utcnow()
                else:
                    last_edited = datetime.fromisoformat(last_edited_str.replace("Z", "+00:00"))
                
                # Upsert the page and its content
                await upsert_page(db, page_id, last_edited)
                await db.commit()
                
                stats["processed"] += 1
                logger.info("✓ Page processed successfully", page_id=page_id)
                
            except Exception as e:
                logger.error("✗ Error processing page", page_id=page_id, error=str(e))
                stats["errors"] += 1
                # Rollback on error
                await db.rollback()
    
    # Process all pages in parallel with concurrency limit
    await asyncio.gather(
        *[process_single_page(page_id) for page_id in DATABASE_IDS],
        return_exceptions=True
    )
    
    logger.info("Notion pages ingestion completed", stats=stats)
    return stats
