-- Migration 004: Link old feedback with query_logs

-- Update feedback to link with most recent query_log for each user
UPDATE feedback f
SET query_log_id = (
    SELECT q.id 
    FROM query_logs q 
    WHERE q.telegram_user_id = f.telegram_user_id 
      AND q.ts <= f.ts
    ORDER BY q.ts DESC 
    LIMIT 1
)
WHERE f.query_log_id IS NULL;

