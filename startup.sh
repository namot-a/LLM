#!/bin/bash
# Startup script for Railway deployment

echo "Starting Notion RAG Bot..."

# Initialize database
echo "Initializing database..."
python init_db.py

# Start the application
echo "Starting application..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

