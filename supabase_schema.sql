-- ============================================================
-- Quiz App — Supabase Schema
-- Run this in Supabase SQL Editor (once, in order)
-- ============================================================

-- 1. SUBJECTS
-- A subject is a top-level topic collection (e.g. "Biológia")
-- user_id = NULL means it's system/seeded content, visible to everyone
CREATE TABLE subjects (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    description TEXT,
    user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 2. CATEGORIES
-- A category is a subdivision within a subject (e.g. "Genetika")
CREATE TABLE categories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id  UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    description TEXT,
    sort_order  INT DEFAULT 0,   -- controls display order
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 3. QUESTIONS
-- Each question belongs to a subject and optionally a category
-- options is a JSONB object: {"a": "text", "b": "text", ...}
-- type: 'multiple_choice' (exactly 1 correct) | 'multiple_correct' (1+ correct)
-- source_question_number: original number from the PDF, for reference
-- user_id = NULL means system/seeded question
CREATE TABLE questions (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id             UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    category_id            UUID REFERENCES categories(id) ON DELETE SET NULL,
    question_number        INT,             -- original number from PDF
    question_text          TEXT NOT NULL,
    type                   TEXT NOT NULL CHECK (type IN ('multiple_choice', 'multiple_correct')),
    options                JSONB NOT NULL,  -- {"a": "...", "b": "...", ...}
    correct_options        TEXT[] NOT NULL, -- ["a", "c"] — stored directly on question for simplicity
    page                   INT,             -- PDF page reference
    user_id                UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at             TIMESTAMPTZ DEFAULT now()
);

-- 4. QUIZ SESSIONS
-- One row per quiz attempt by a user
-- settings stores what the user configured: {question_count, time_limit_seconds, category_ids, subject_id}
-- score and total_questions filled in when quiz is submitted
CREATE TABLE quiz_sessions (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    subject_id       UUID REFERENCES subjects(id) ON DELETE SET NULL,
    settings         JSONB NOT NULL DEFAULT '{}',
    mode             TEXT NOT NULL CHECK (mode IN ('review', 'custom_quiz')),
    score            INT,                  -- number of correct answers
    total_questions  INT,                  -- total questions in session
    started_at       TIMESTAMPTZ DEFAULT now(),
    completed_at     TIMESTAMPTZ,          -- NULL if abandoned/in-progress
    time_spent_secs  INT                   -- how long the user actually took
);

-- 5. QUIZ ANSWERS
-- One row per question answered within a session
CREATE TABLE quiz_answers (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id       UUID NOT NULL REFERENCES quiz_sessions(id) ON DELETE CASCADE,
    question_id      UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    selected_options TEXT[] NOT NULL,      -- what the user picked
    is_correct       BOOLEAN NOT NULL,
    answered_at      TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- INDEXES (for performance on common queries)
-- ============================================================
CREATE INDEX idx_questions_subject     ON questions(subject_id);
CREATE INDEX idx_questions_category    ON questions(category_id);
CREATE INDEX idx_questions_user        ON questions(user_id);
CREATE INDEX idx_quiz_sessions_user    ON quiz_sessions(user_id);
CREATE INDEX idx_quiz_answers_session  ON quiz_answers(session_id);

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- Enables per-user data isolation for sensitive tables
-- ============================================================

ALTER TABLE subjects        ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories      ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions       ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_sessions   ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_answers    ENABLE ROW LEVEL SECURITY;

-- SUBJECTS: users can read system content (user_id IS NULL) and their own
CREATE POLICY "read subjects" ON subjects
    FOR SELECT USING (user_id IS NULL OR user_id = auth.uid());

CREATE POLICY "insert own subjects" ON subjects
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "update own subjects" ON subjects
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "delete own subjects" ON subjects
    FOR DELETE USING (auth.uid() = user_id);

-- CATEGORIES: same logic as subjects (inherits via subject_id)
CREATE POLICY "read categories" ON categories
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM subjects s
            WHERE s.id = categories.subject_id
            AND (s.user_id IS NULL OR s.user_id = auth.uid())
        )
    );

CREATE POLICY "manage own categories" ON categories
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM subjects s
            WHERE s.id = categories.subject_id
            AND s.user_id = auth.uid()
        )
    );

-- QUESTIONS: read all system + own; write only own
CREATE POLICY "read questions" ON questions
    FOR SELECT USING (user_id IS NULL OR user_id = auth.uid());

CREATE POLICY "insert own questions" ON questions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "update own questions" ON questions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "delete own questions" ON questions
    FOR DELETE USING (auth.uid() = user_id);

-- QUIZ SESSIONS: fully private, user sees only their own
CREATE POLICY "own sessions only" ON quiz_sessions
    FOR ALL USING (auth.uid() = user_id);

-- QUIZ ANSWERS: accessible via session ownership
CREATE POLICY "own answers only" ON quiz_answers
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM quiz_sessions qs
            WHERE qs.id = quiz_answers.session_id
            AND qs.user_id = auth.uid()
        )
    );

CREATE TABLE question_review_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'unreviewed' CHECK (status IN ('unreviewed', 'repeat', 'done')),
    last_reviewed_at TIMESTAMPTZ,
    UNIQUE(user_id, question_id)
);

ALTER TABLE question_review_state ENABLE ROW LEVEL SECURITY;

CREATE POLICY "own review state only" ON question_review_state
    FOR ALL USING (auth.uid() = user_id);

CREATE INDEX idx_review_state_user ON question_review_state(user_id);
CREATE INDEX idx_review_state_question ON question_review_state(question_id);
