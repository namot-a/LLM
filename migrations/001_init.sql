-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notion_page_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    last_edited TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create chunks table
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    heading_path TEXT,
    content TEXT NOT NULL,
    embedding VECTOR(1536), -- Will be updated based on EMBEDDING_DIM
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create query_logs table
CREATE TABLE IF NOT EXISTS query_logs (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    telegram_user_id BIGINT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    model TEXT,
    cost_usd NUMERIC(10,4),
    processing_time_ms INTEGER
);

-- Create feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    telegram_user_id BIGINT NOT NULL,
    message_id BIGINT,
    query_log_id BIGINT REFERENCES query_logs(id),
    rating TEXT NOT NULL CHECK (rating IN ('good', 'bad')),
    comment TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_notion_page_id ON documents(notion_page_id);
CREATE INDEX IF NOT EXISTS idx_documents_last_edited ON documents(last_edited);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_query_logs_ts ON query_logs(ts);
CREATE INDEX IF NOT EXISTS idx_query_logs_user_id ON query_logs(telegram_user_id);

CREATE INDEX IF NOT EXISTS idx_feedback_ts ON feedback(ts);
CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback(rating);
