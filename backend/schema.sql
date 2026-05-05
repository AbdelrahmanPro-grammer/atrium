-- Atrium v0.1 schema
-- Three tables: professors, courses, insights
-- Insights link a professor to a course with student-written text and optional ratings.

CREATE TABLE IF NOT EXISTS professors (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    department  TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS insights (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    professor_id  INTEGER NOT NULL,
    course_id     INTEGER NOT NULL,
    text          TEXT NOT NULL,
    workload      TEXT,
    clarity       INTEGER,
    fairness      INTEGER,
    helpful_count INTEGER DEFAULT 0,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (professor_id) REFERENCES professors(id),
    FOREIGN KEY (course_id)    REFERENCES courses(id),
    CHECK (workload IS NULL OR workload IN ('light', 'moderate', 'heavy')),
    CHECK (clarity IS NULL OR (clarity BETWEEN 1 AND 5)),
    CHECK (fairness IS NULL OR (fairness BETWEEN 1 AND 5))
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_insights_professor ON insights(professor_id);
CREATE INDEX IF NOT EXISTS idx_insights_course    ON insights(course_id);
CREATE INDEX IF NOT EXISTS idx_insights_created   ON insights(created_at DESC);