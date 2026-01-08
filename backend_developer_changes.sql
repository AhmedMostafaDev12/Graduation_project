-- ============================================================================
-- Backend Developer's New Changes - Database Migration
-- ============================================================================
-- This adds the new features the backend developer created
-- ============================================================================

-- Step 1: Add integration_provider_task_id column to tasks table
-- ============================================================================
-- This is a unified column for ALL external integration task IDs
-- (Google Classroom, Trello, etc.)

ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS integration_provider_task_id VARCHAR(255) UNIQUE;

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_tasks_integration_provider_id
ON tasks(integration_provider_task_id);

-- ============================================================================
-- Step 2: Create temp_trello_tokens table
-- ============================================================================
-- This table stores temporary OAuth tokens during Trello authentication flow

CREATE TABLE IF NOT EXISTS temp_trello_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    oauth_token VARCHAR(255) NOT NULL,
    oauth_token_secret VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add index for faster user lookups
CREATE INDEX IF NOT EXISTS idx_temp_trello_tokens_user_id
ON temp_trello_tokens(user_id);

-- Add index on oauth_token for faster token lookups
CREATE INDEX IF NOT EXISTS idx_temp_trello_tokens_oauth_token
ON temp_trello_tokens(oauth_token);

-- ============================================================================
-- Verification
-- ============================================================================

-- Check integration_provider_task_id column was added
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'tasks' AND column_name = 'integration_provider_task_id'
    ) THEN
        RAISE NOTICE '✓ integration_provider_task_id column added to tasks table';
    ELSE
        RAISE WARNING '⚠ integration_provider_task_id column NOT found in tasks table';
    END IF;
END $$;

-- Check temp_trello_tokens table was created
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'temp_trello_tokens'
    ) THEN
        RAISE NOTICE '✓ temp_trello_tokens table created';
    ELSE
        RAISE WARNING '⚠ temp_trello_tokens table NOT created';
    END IF;
END $$;

-- Show updated tasks table structure
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'tasks'
ORDER BY ordinal_position;

COMMIT;

-- ============================================================================
-- COMPLETE
-- ============================================================================
