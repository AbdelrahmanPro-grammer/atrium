"""
Atrium — Database access layer.

This module is the single source of truth for talking to SQLite.
All other modules (routes, seed scripts, tests) should call functions here
rather than writing SQL directly. This keeps SQL contained and testable.
"""

import sqlite3
from pathlib import Path
from typing import Optional


# The database file lives one level up from this file (in /atrium/atrium.db).
# Using a Path object keeps this OS-agnostic (works on Windows, Mac, Linux).
DB_PATH = Path(__file__).parent.parent / "atrium.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """
    Open a new connection to the SQLite database.

    Two important settings:
      - row_factory = sqlite3.Row makes rows behave like dictionaries
        (so we can write row["name"] instead of row[0]). Easier to read.
      - foreign_keys = ON enforces foreign key constraints. SQLite has them
        OFF by default for historical reasons — we always want them on.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """
    Create all tables by executing schema.sql.
    Safe to run multiple times — schema uses CREATE TABLE IF NOT EXISTS.
    """
    with get_connection() as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
    print(f"Database initialized at {DB_PATH}")


# ---------------------------------------------------------------------------
# Professors
# ---------------------------------------------------------------------------

def create_professor(name: str, department: str) -> int:
    """Insert a professor and return its new id."""
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO professors (name, department) VALUES (?, ?)",
            (name, department),
        )
        return cursor.lastrowid


def get_all_professors() -> list[dict]:
    """Return every professor, sorted by name."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, department FROM professors ORDER BY name"
        ).fetchall()
        return [dict(row) for row in rows]


def get_professor(professor_id: int) -> Optional[dict]:
    """Return a single professor by id, or None if not found."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, department FROM professors WHERE id = ?",
            (professor_id,),
        ).fetchone()
        return dict(row) if row else None


# ---------------------------------------------------------------------------
# Courses
# ---------------------------------------------------------------------------

def create_course(code: str, name: str) -> int:
    """Insert a course and return its new id."""
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO courses (code, name) VALUES (?, ?)",
            (code, name),
        )
        return cursor.lastrowid


def get_all_courses() -> list[dict]:
    """Return every course, sorted by code."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, code, name FROM courses ORDER BY code"
        ).fetchall()
        return [dict(row) for row in rows]


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

def create_insight(
    professor_id: int,
    course_id: int,
    text: str,
    workload: Optional[str] = None,
    clarity: Optional[int] = None,
    fairness: Optional[int] = None,
) -> int:
    """
    Create a new insight. Only text is required; ratings are optional.
    Returns the id of the new insight.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO insights
                (professor_id, course_id, text, workload, clarity, fairness)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (professor_id, course_id, text, workload, clarity, fairness),
        )
        return cursor.lastrowid


def get_insights_for_professor(professor_id: int) -> list[dict]:
    """
    Return all insights for a single professor, joined with course info,
    sorted by most recent first.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                i.id, i.text, i.workload, i.clarity, i.fairness,
                i.helpful_count, i.created_at,
                c.code AS course_code, c.name AS course_name
            FROM insights i
            JOIN courses c ON c.id = i.course_id
            WHERE i.professor_id = ?
            ORDER BY i.created_at DESC
            """,
            (professor_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_recent_insights(limit: int = 20) -> list[dict]:
    """
    Return the most recent insights across all professors,
    joined with professor and course info.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                i.id, i.text, i.workload, i.clarity, i.fairness,
                i.helpful_count, i.created_at,
                p.id AS professor_id, p.name AS professor_name,
                c.code AS course_code, c.name AS course_name
            FROM insights i
            JOIN professors p ON p.id = i.professor_id
            JOIN courses    c ON c.id = i.course_id
            ORDER BY i.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def increment_helpful_count(insight_id: int) -> bool:
    """
    Increment the helpful_count on an insight by 1.
    Returns True if the insight existed and was updated, False otherwise.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE insights SET helpful_count = helpful_count + 1 WHERE id = ?",
            (insight_id,),
        )
        return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# CLI entry point — lets us run `python backend/db.py` to initialize the DB
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()