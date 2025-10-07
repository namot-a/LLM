#!/usr/bin/env python3
"""Entry point for running the application."""
import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.log_level == "DEBUG",
        log_level=settings.log_level.lower()
    )
