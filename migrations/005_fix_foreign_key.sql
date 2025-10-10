-- Migration 005: Fix foreign key constraint

-- Drop existing foreign key
ALTER TABLE feedback DROP CONSTRAINT IF EXISTS feedback_query_log_id_fkey;

-- Add foreign key with ON DELETE SET NULL
ALTER TABLE feedback 
ADD CONSTRAINT feedback_query_log_id_fkey 
FOREIGN KEY (query_log_id) 
REFERENCES query_logs(id) 
ON DELETE SET NULL;

