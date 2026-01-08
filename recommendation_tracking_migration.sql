-- ============================================================================
-- RECOMMENDATION TRACKING DATABASE SCHEMA
-- ============================================================================
--
-- This migration adds tables to track AI-generated recommendations,
-- their application status, and user feedback.
--
-- Run this AFTER the main database_migration.sql
--
-- ============================================================================

-- Table: recommendations
-- Stores all AI-generated recommendations for users
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    burnout_analysis_id INTEGER,  -- Link to the burnout_analyses table

    -- Recommendation content
    title VARCHAR(255) NOT NULL,
    priority VARCHAR(50),  -- HIGH, MEDIUM, LOW
    description TEXT,
    action_steps JSONB,  -- Array of action steps
    expected_impact TEXT,

    -- Metadata
    generated_at TIMESTAMP DEFAULT NOW(),
    generated_by VARCHAR(100) DEFAULT 'RAG+LLM',  -- Which system generated it
    llm_model VARCHAR(100),  -- e.g., "llama3.1:8b"
    strategies_retrieved INTEGER,  -- How many strategies from vector DB
    generation_time_seconds FLOAT,

    -- Categorization
    category VARCHAR(100),  -- e.g., "meeting_overload", "work_life_balance"
    burnout_component VARCHAR(50),  -- Which component it addresses: workload, sentiment, etc.

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT valid_priority CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW'))
);

CREATE INDEX idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX idx_recommendations_generated_at ON recommendations(generated_at DESC);
CREATE INDEX idx_recommendations_burnout_analysis_id ON recommendations(burnout_analysis_id);


-- Table: recommendation_applications
-- Tracks when recommendations are applied and their outcomes
CREATE TABLE IF NOT EXISTS recommendation_applications (
    id SERIAL PRIMARY KEY,
    recommendation_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,

    -- Application details
    applied_at TIMESTAMP DEFAULT NOW(),
    applied_by VARCHAR(100),  -- 'user' or 'auto'

    -- What was created/modified
    tasks_created INTEGER DEFAULT 0,
    task_ids JSONB,  -- Array of created task IDs
    calendar_events_created INTEGER DEFAULT 0,
    tasks_modified INTEGER DEFAULT 0,

    -- Effectiveness tracking
    status VARCHAR(50) DEFAULT 'applied',  -- applied, in_progress, completed, cancelled
    completion_rate FLOAT,  -- % of action steps completed (0-100)
    completed_at TIMESTAMP,
    time_to_complete_days INTEGER,

    -- User feedback
    effectiveness_rating INTEGER,  -- 1-5 stars
    user_feedback TEXT,
    feedback_submitted_at TIMESTAMP,

    -- Impact measurement
    burnout_score_before INTEGER,  -- User's burnout score before applying
    burnout_score_after INTEGER,   -- User's burnout score after completion
    burnout_improvement INTEGER GENERATED ALWAYS AS (burnout_score_before - burnout_score_after) STORED,

    FOREIGN KEY (recommendation_id) REFERENCES recommendations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT valid_status CHECK (status IN ('applied', 'in_progress', 'completed', 'cancelled')),
    CONSTRAINT valid_rating CHECK (effectiveness_rating IS NULL OR (effectiveness_rating >= 1 AND effectiveness_rating <= 5))
);

CREATE INDEX idx_recommendation_applications_recommendation_id ON recommendation_applications(recommendation_id);
CREATE INDEX idx_recommendation_applications_user_id ON recommendation_applications(user_id);
CREATE INDEX idx_recommendation_applications_applied_at ON recommendation_applications(applied_at DESC);
CREATE INDEX idx_recommendation_applications_status ON recommendation_applications(status);


-- Table: recommendation_action_items
-- Tracks individual action steps from recommendations
CREATE TABLE IF NOT EXISTS recommendation_action_items (
    id SERIAL PRIMARY KEY,
    recommendation_id INTEGER NOT NULL,
    task_id INTEGER,  -- Link to tasks table if action became a task

    -- Action details
    action_text TEXT NOT NULL,
    action_order INTEGER,  -- 1st, 2nd, 3rd action step

    -- Completion tracking
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (recommendation_id) REFERENCES recommendations(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
);

CREATE INDEX idx_recommendation_action_items_recommendation_id ON recommendation_action_items(recommendation_id);
CREATE INDEX idx_recommendation_action_items_task_id ON recommendation_action_items(task_id);
CREATE INDEX idx_recommendation_action_items_completed ON recommendation_action_items(completed);


-- Table: recommendation_feedback
-- Additional detailed feedback on recommendations
CREATE TABLE IF NOT EXISTS recommendation_feedback (
    id SERIAL PRIMARY KEY,
    recommendation_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,

    -- Feedback details
    helpful BOOLEAN,
    reason VARCHAR(255),  -- Why it was/wasn't helpful

    -- Which action steps were most helpful
    most_helpful_action_step INTEGER,  -- Index of the most helpful step
    least_helpful_action_step INTEGER,  -- Index of the least helpful step

    -- Free-form feedback
    comments TEXT,

    -- Metadata
    submitted_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (recommendation_id) REFERENCES recommendations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_recommendation_feedback_recommendation_id ON recommendation_feedback(recommendation_id);
CREATE INDEX idx_recommendation_feedback_user_id ON recommendation_feedback(user_id);


-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

-- View: recommendation_effectiveness
-- Shows which recommendations are most effective
CREATE OR REPLACE VIEW recommendation_effectiveness AS
SELECT
    r.id AS recommendation_id,
    r.title,
    r.category,
    r.priority,
    COUNT(ra.id) AS times_applied,
    AVG(ra.effectiveness_rating) AS avg_rating,
    AVG(ra.completion_rate) AS avg_completion_rate,
    AVG(ra.burnout_improvement) AS avg_burnout_improvement,
    COUNT(CASE WHEN ra.status = 'completed' THEN 1 END) AS times_completed,
    AVG(ra.time_to_complete_days) AS avg_days_to_complete
FROM recommendations r
LEFT JOIN recommendation_applications ra ON r.id = ra.recommendation_id
GROUP BY r.id, r.title, r.category, r.priority
ORDER BY avg_burnout_improvement DESC NULLS LAST;


-- View: user_recommendation_history
-- Shows recommendation history for a user
CREATE OR REPLACE VIEW user_recommendation_history AS
SELECT
    r.id AS recommendation_id,
    r.user_id,
    r.title,
    r.priority,
    r.generated_at,
    ra.applied_at,
    ra.status,
    ra.effectiveness_rating,
    ra.burnout_improvement,
    ra.tasks_created,
    ra.completion_rate
FROM recommendations r
LEFT JOIN recommendation_applications ra ON r.id = ra.recommendation_id
ORDER BY r.user_id, r.generated_at DESC;


-- ============================================================================
-- SAMPLE QUERIES
-- ============================================================================

-- Get all recommendations for a user
-- SELECT * FROM recommendations WHERE user_id = 1 ORDER BY generated_at DESC;

-- Get applied recommendations with outcomes
-- SELECT * FROM user_recommendation_history WHERE user_id = 1 AND applied_at IS NOT NULL;

-- Get most effective recommendations globally
-- SELECT * FROM recommendation_effectiveness ORDER BY avg_burnout_improvement DESC LIMIT 10;

-- Get pending action items for a user
-- SELECT ai.*
-- FROM recommendation_action_items ai
-- JOIN recommendations r ON ai.recommendation_id = r.id
-- WHERE r.user_id = 1 AND ai.completed = FALSE;

-- Get recommendations that haven't been applied yet
-- SELECT r.*
-- FROM recommendations r
-- LEFT JOIN recommendation_applications ra ON r.id = ra.recommendation_id
-- WHERE r.user_id = 1 AND ra.id IS NULL
-- ORDER BY r.generated_at DESC;
