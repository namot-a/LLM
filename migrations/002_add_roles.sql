-- Migration 002: Add role-based access control
-- Add allowed_roles column to chunks table
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS allowed_roles TEXT[];

-- Add allowed_roles column to notion_pages table
ALTER TABLE notion_pages ADD COLUMN IF NOT EXISTS allowed_roles TEXT[] DEFAULT ARRAY['Recruiter', 'Team Lead', 'Head'];

-- Create index for faster role-based filtering
CREATE INDEX IF NOT EXISTS idx_chunks_allowed_roles ON chunks USING GIN (allowed_roles);

-- Update existing notion_pages to have default roles if NULL
UPDATE notion_pages SET allowed_roles = ARRAY['Recruiter', 'Team Lead', 'Head'] WHERE allowed_roles IS NULL;

