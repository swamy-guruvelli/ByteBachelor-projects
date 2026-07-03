-- Run with:
-- psql "$DATABASE_URL" -v project_id="'<PROJECT_ID>'" -f experiments/query-plans.sql

\echo 'Indexed plan'
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title, status
FROM tasks
WHERE project_id = :project_id::uuid AND status = 'todo'
ORDER BY created_at DESC, id DESC
LIMIT 50;

BEGIN;
DROP INDEX ix_tasks_project_status_created;

\echo 'Unindexed plan (index removal is rolled back)'
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title, status
FROM tasks
WHERE project_id = :project_id::uuid AND status = 'todo'
ORDER BY created_at DESC, id DESC
LIMIT 50;

ROLLBACK;

