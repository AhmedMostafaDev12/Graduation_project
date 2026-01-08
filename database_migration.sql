-- ============================================================================
-- Sentry AI - Database Migration Script
-- ============================================================================
-- Purpose: Add backend tables and link them to existing AI tables
-- Strategy: Keep AI tasks table, add 3 backend tables, create uploads table
-- ============================================================================

-- Step 1: Create users table (PRIMARY TABLE)
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    birthday DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    refresh_token TEXT,
    refresh_token_expiry TIMESTAMP WITH TIME ZONE,
    is_verified BOOLEAN DEFAULT FALSE
);

-- Index for faster email lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_verified ON users(is_verified);

-- ============================================================================
-- Step 2: Create auth_providers table
-- ============================================================================
CREATE TABLE IF NOT EXISTS auth_providers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,  -- 'google', 'facebook', 'apple', 'email'
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_auth_providers_user_id ON auth_providers(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_providers_provider ON auth_providers(provider);

-- Prevent duplicate provider entries per user
CREATE UNIQUE INDEX IF NOT EXISTS idx_auth_providers_user_provider
ON auth_providers(user_id, provider);

-- ============================================================================
-- Step 3: Create integrations table
-- ============================================================================
CREATE TABLE IF NOT EXISTS integrations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service VARCHAR(100) NOT NULL,  -- 'gmail', 'google_calendar', 'google_tasks', 'zoom_meetings'
    access_token TEXT,
    refresh_token TEXT,
    expiry TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_integrations_user_id ON integrations(user_id);
CREATE INDEX IF NOT EXISTS idx_integrations_service ON integrations(service);

-- Prevent duplicate service entries per user
CREATE UNIQUE INDEX IF NOT EXISTS idx_integrations_user_service
ON integrations(user_id, service);

-- ============================================================================
-- Step 4: Create uploads table (NEW)
-- ============================================================================
CREATE TABLE IF NOT EXISTS uploads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- File metadata
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100),

    -- Processing metadata
    upload_type VARCHAR(50) NOT NULL,  -- 'audio', 'document', 'image', 'video', 'handwritten', 'notebook'
    processing_status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed'
    extraction_result JSONB,  -- Store extracted tasks or processing results

    -- Session tracking
    session_id VARCHAR(100),

    -- Timestamps
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,

    -- Soft delete
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_uploads_user_id ON uploads(user_id);
CREATE INDEX IF NOT EXISTS idx_uploads_session_id ON uploads(session_id);
CREATE INDEX IF NOT EXISTS idx_uploads_status ON uploads(processing_status);
CREATE INDEX IF NOT EXISTS idx_uploads_type ON uploads(upload_type);
CREATE INDEX IF NOT EXISTS idx_uploads_deleted_at ON uploads(deleted_at);

-- ============================================================================
-- Step 5: Add foreign key to existing user_profiles table
-- ============================================================================
-- Link user_profiles to users table
DO $$
BEGIN
    -- Check if foreign key doesn't already exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_user_profiles_user_id'
    ) THEN
        ALTER TABLE user_profiles
        ADD CONSTRAINT fk_user_profiles_user_id
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Ensure user_profiles.user_id is unique (one profile per user)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'idx_user_profiles_user_id_unique'
    ) THEN
        CREATE UNIQUE INDEX idx_user_profiles_user_id_unique ON user_profiles(user_id);
    END IF;
END $$;

-- ============================================================================
-- Step 6: Add foreign key to existing tasks table
-- ============================================================================
-- Link tasks to users table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_tasks_user_id'
    ) THEN
        ALTER TABLE tasks
        ADD CONSTRAINT fk_tasks_user_id
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Add index if not exists
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);

-- ============================================================================
-- Step 7: Add foreign key to existing qualitative_data table
-- ============================================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_qualitative_data_user_id'
    ) THEN
        ALTER TABLE qualitative_data
        ADD CONSTRAINT fk_qualitative_data_user_id
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_qualitative_data_user_id ON qualitative_data(user_id);

-- ============================================================================
-- Step 8: Update backend's tasks table model to match AI schema
-- ============================================================================
-- NOTE: The backend's Task model needs to be updated to use the AI schema
-- The AI tasks table already exists with this schema:
--   - id (PK)
--   - title
--   - user_id
--   - task_type ('task' or 'meeting')
--   - status
--   - priority
--   - due_date
--   - assigned_to
--   - can_delegate
--   - estimated_hours
--   - start_time (for meetings)
--   - end_time (for meetings)
--   - attendees
--   - is_recurring
--   - is_optional
--   - created_at
--   - updated_at

-- Add missing columns to tasks table if they don't exist (for backend compatibility)
DO $$
BEGIN
    -- Add 'source' column for backend (tracks where task came from)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'tasks' AND column_name = 'source'
    ) THEN
        ALTER TABLE tasks ADD COLUMN source VARCHAR(50);
        -- Set default for existing rows
        UPDATE tasks SET source = 'sentry' WHERE source IS NULL;
    END IF;

    -- Add 'description' column for backend
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'tasks' AND column_name = 'description'
    ) THEN
        ALTER TABLE tasks ADD COLUMN description TEXT DEFAULT '';
    END IF;

    -- Add 'category' column for backend
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'tasks' AND column_name = 'category'
    ) THEN
        ALTER TABLE tasks ADD COLUMN category VARCHAR(100);
    END IF;

    -- Add Google Tasks integration columns
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'tasks' AND column_name = 'google_task_id'
    ) THEN
        ALTER TABLE tasks ADD COLUMN google_task_id VARCHAR(255) UNIQUE;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'tasks' AND column_name = 'google_tasklist_id'
    ) THEN
        ALTER TABLE tasks ADD COLUMN google_tasklist_id VARCHAR(255);
    END IF;

    -- Rename 'due_date' to 'deadline' for backend compatibility (optional)
    -- OR just use due_date in backend - recommend keeping AI's 'due_date'
END $$;

-- Add indexes for new columns
CREATE INDEX IF NOT EXISTS idx_tasks_source ON tasks(source);
CREATE INDEX IF NOT EXISTS idx_tasks_google_task_id ON tasks(google_task_id);

-- ============================================================================
-- Verification Queries
-- ============================================================================
-- Run these to verify the migration

-- Show all tables
-- SELECT table_name FROM information_schema.tables
-- WHERE table_schema = 'public' ORDER BY table_name;

-- Show all foreign keys
-- SELECT
--     tc.table_name,
--     tc.constraint_name,
--     kcu.column_name,
--     ccu.table_name AS foreign_table_name,
--     ccu.column_name AS foreign_column_name
-- FROM information_schema.table_constraints AS tc
-- JOIN information_schema.key_column_usage AS kcu
--     ON tc.constraint_name = kcu.constraint_name
-- JOIN information_schema.constraint_column_usage AS ccu
--     ON ccu.constraint_name = tc.constraint_name
-- WHERE tc.constraint_type = 'FOREIGN KEY'
-- ORDER BY tc.table_name;

-- Show tasks table structure
-- SELECT column_name, data_type, is_nullable, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'tasks'
-- ORDER BY ordinal_position;

-- ============================================================================
-- COMPLETE
-- ============================================================================

COMMIT;

-- Print success message
DO $$
BEGIN
    RAISE NOTICE '✅ Database migration completed successfully!';
    RAISE NOTICE '';
    RAISE NOTICE 'Created tables:';
    RAISE NOTICE '  - users (PRIMARY)';
    RAISE NOTICE '  - auth_providers (FK to users)';
    RAISE NOTICE '  - integrations (FK to users)';
    RAISE NOTICE '  - uploads (FK to users)';
    RAISE NOTICE '';
    RAISE NOTICE 'Updated tables:';
    RAISE NOTICE '  - user_profiles (added FK to users)';
    RAISE NOTICE '  - tasks (added FK to users, added backend columns)';
    RAISE NOTICE '  - qualitative_data (added FK to users)';
    RAISE NOTICE '';
    RAISE NOTICE 'Relationship structure:';
    RAISE NOTICE '  users (PRIMARY)';
    RAISE NOTICE '  ├── user_profiles (user_id FK)';
    RAISE NOTICE '  │   ├── burnout_analyses (user_profile_id FK)';
    RAISE NOTICE '  │   ├── user_preferences (user_profile_id FK)';
    RAISE NOTICE '  │   ├── user_constraints (user_profile_id FK)';
    RAISE NOTICE '  │   └── user_behavioral_profiles (user_profile_id FK)';
    RAISE NOTICE '  ├── tasks (user_id FK)';
    RAISE NOTICE '  ├── qualitative_data (user_id FK)';
    RAISE NOTICE '  ├── auth_providers (user_id FK)';
    RAISE NOTICE '  ├── integrations (user_id FK)';
    RAISE NOTICE '  └── uploads (user_id FK)';
END $$;
