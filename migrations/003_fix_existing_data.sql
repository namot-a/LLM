-- Migration 003: Fix existing data

-- Update all existing query_logs to have has_answer = true (they already have answers)
UPDATE query_logs 
SET has_answer = TRUE 
WHERE has_answer IS NULL;

-- Mark queries as failed if answer contains "не нашла" or "недоступна"
UPDATE query_logs 
SET has_answer = FALSE 
WHERE (answer LIKE '%не нашла%' OR answer LIKE '%недоступна%') 
  AND has_answer IS NOT NULL;

