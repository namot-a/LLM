"""Database models with improved structure."""
import os
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, BigInteger, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .db import Base

# Get embedding dimension from environment
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", 1536))


class Document(Base):
    """Document model representing a Notion page."""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notion_page_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    last_edited = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title='{self.title[:50]}...')>"


class Chunk(Base):
    """Chunk model representing a text fragment with embedding."""
    __tablename__ = "chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    heading_path = Column(Text)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    # Indexes for better performance
    __table_args__ = (
        Index("idx_chunks_document_id", "document_id"),
        Index("idx_chunks_embedding", "embedding", postgresql_using="ivfflat", 
              postgresql_with={"lists": 100}, postgresql_ops={"embedding": "vector_cosine_ops"}),
    )
    
    def __repr__(self) -> str:
        return f"<Chunk(id={self.id}, index={self.chunk_index}, content='{self.content[:30]}...')>"


class QueryLog(Base):
    """Query log for tracking usage and costs."""
    __tablename__ = "query_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ts = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    telegram_user_id = Column(BigInteger, nullable=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    model = Column(String, nullable=True)
    cost_usd = Column(Numeric(10, 4), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)  # Processing time in milliseconds
    
    def __repr__(self) -> str:
        return f"<QueryLog(id={self.id}, user={self.telegram_user_id}, tokens={self.prompt_tokens})>"


class Feedback(Base):
    """User feedback on bot responses."""
    __tablename__ = "feedback"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ts = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    telegram_user_id = Column(BigInteger, nullable=False, index=True)
    message_id = Column(BigInteger, nullable=True)
    query_log_id = Column(BigInteger, ForeignKey("query_logs.id"), nullable=True)
    rating = Column(String, nullable=False)  # 'good' or 'bad'
    comment = Column(Text, nullable=True)
    
    # Relationships
    query_log = relationship("QueryLog", foreign_keys=[query_log_id])
    
    def __repr__(self) -> str:
        return f"<Feedback(id={self.id}, user={self.telegram_user_id}, rating={self.rating})>"
