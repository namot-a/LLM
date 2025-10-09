#!/usr/bin/env python3
"""Test Notion API connection."""
import asyncio
from notion_client import AsyncClient
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)


async def test_notion():
    """Test Notion connection and database access."""
    try:
        notion = AsyncClient(auth=settings.notion_token)
        database_ids = settings.get_database_ids()
        
        print(f"\n=== Testing Notion API ===")
        print(f"Total databases to check: {len(database_ids)}")
        
        accessible = 0
        errors = 0
        
        for i, db_id in enumerate(database_ids[:5], 1):  # Test first 5
            try:
                print(f"\n[{i}] Testing database: {db_id}")
                
                # Try to query the database
                response = await notion.databases.query(database_id=db_id, page_size=1)
                pages_count = len(response.get("results", []))
                
                print(f"    ✅ Accessible - {pages_count} pages found")
                accessible += 1
                
            except Exception as e:
                print(f"    ❌ Error: {str(e)[:100]}")
                errors += 1
        
        print(f"\n=== Summary ===")
        print(f"Accessible: {accessible}")
        print(f"Errors: {errors}")
        
    except Exception as e:
        logger.error("Test failed", error=str(e))
        raise


if __name__ == "__main__":
    asyncio.run(test_notion())

