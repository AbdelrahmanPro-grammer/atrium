"""
Tests for the data access layer (backend/db.py).

We focus on the data layer because it contains the most logic that could
silently break: the optional fields, the joins, the foreign-key relationships,
and the helpful-count increment.

Each test uses the `temp_db` fixture, which gives it a fresh, empty database.
"""

import pytest


# ---------------------------------------------------------------------------
# Professor and course CRUD
# ---------------------------------------------------------------------------

def test_create_and_list_professor(temp_db):
    """A created professor should appear in the full list."""
    pid = temp_db.create_professor("Dr. Test", "Computer Science")
    assert isinstance(pid, int)

    professors = temp_db.get_all_professors()
    assert len(professors) == 1
    assert professors[0]["name"] == "Dr. Test"
    assert professors[0]["department"] == "Computer Science"


def test_get_professor_returns_none_for_missing_id(temp_db):
    """Looking up a non-existent professor should return None, not raise."""
    assert temp_db.get_professor(999) is None


def test_create_course(temp_db):
    """A created course should be retrievable in the full list, sorted by code."""
    temp_db.create_course("CMPS 251", "Object-Oriented Programming")
    temp_db.create_course("CMPS 151", "Programming Concepts")

    courses = temp_db.get_all_courses()
    codes = [c["code"] for c in courses]
    assert codes == ["CMPS 151", "CMPS 251"]


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

def test_create_insight_with_only_required_fields(temp_db):
    """Insights should be creatable without any optional ratings."""
    pid = temp_db.create_professor("Dr. Test", "CS")
    cid = temp_db.create_course("CMPS 101", "Intro")

    insight_id = temp_db.create_insight(
        professor_id=pid,
        course_id=cid,
        text="A simple insight without ratings.",
    )

    insights = temp_db.get_insights_for_professor(pid)
    assert len(insights) == 1
    assert insights[0]["id"] == insight_id
    assert insights[0]["text"] == "A simple insight without ratings."
    assert insights[0]["workload"] is None
    assert insights[0]["clarity"] is None
    assert insights[0]["fairness"] is None


def test_create_insight_with_all_fields(temp_db):
    """All optional fields should be persisted when provided."""
    pid = temp_db.create_professor("Dr. Test", "CS")
    cid = temp_db.create_course("CMPS 101", "Intro")

    temp_db.create_insight(
        professor_id=pid,
        course_id=cid,
        text="Detailed insight.",
        workload="moderate",
        clarity=4,
        fairness=5,
    )

    insights = temp_db.get_insights_for_professor(pid)
    assert insights[0]["workload"] == "moderate"
    assert insights[0]["clarity"] == 4
    assert insights[0]["fairness"] == 5


def test_insights_for_professor_includes_course_info(temp_db):
    """get_insights_for_professor should join with courses and return code/name."""
    pid = temp_db.create_professor("Dr. Test", "CS")
    cid = temp_db.create_course("CMPS 351", "Database Systems")

    temp_db.create_insight(professor_id=pid, course_id=cid, text="Note.")

    insights = temp_db.get_insights_for_professor(pid)
    assert insights[0]["course_code"] == "CMPS 351"
    assert insights[0]["course_name"] == "Database Systems"


# ---------------------------------------------------------------------------
# Helpful count
# ---------------------------------------------------------------------------

def test_increment_helpful_count(temp_db):
    """Incrementing a real insight should return True and bump the count."""
    pid = temp_db.create_professor("Dr. Test", "CS")
    cid = temp_db.create_course("CMPS 101", "Intro")
    insight_id = temp_db.create_insight(professor_id=pid, course_id=cid, text="X")

    # Initial count is zero
    insights = temp_db.get_insights_for_professor(pid)
    assert insights[0]["helpful_count"] == 0

    # Two increments → count of 2
    assert temp_db.increment_helpful_count(insight_id) is True
    assert temp_db.increment_helpful_count(insight_id) is True

    insights = temp_db.get_insights_for_professor(pid)
    assert insights[0]["helpful_count"] == 2


def test_increment_helpful_count_returns_false_for_missing_id(temp_db):
    """Trying to upvote a non-existent insight should return False, not raise."""
    assert temp_db.increment_helpful_count(999) is False


# ---------------------------------------------------------------------------
# Recent insights feed
# ---------------------------------------------------------------------------

def test_get_recent_insights_returns_most_recent_first(temp_db):
    """The recent insights feed should sort newest first."""
    pid = temp_db.create_professor("Dr. Test", "CS")
    cid = temp_db.create_course("CMPS 101", "Intro")

    temp_db.create_insight(professor_id=pid, course_id=cid, text="First")
    temp_db.create_insight(professor_id=pid, course_id=cid, text="Second")
    temp_db.create_insight(professor_id=pid, course_id=cid, text="Third")

    recent = temp_db.get_recent_insights(limit=10)
    texts = [r["text"] for r in recent]
    assert texts == ["Third", "Second", "First"]


def test_get_recent_insights_respects_limit(temp_db):
    """The `limit` parameter should cap the number of returned insights."""
    pid = temp_db.create_professor("Dr. Test", "CS")
    cid = temp_db.create_course("CMPS 101", "Intro")

    for i in range(5):
        temp_db.create_insight(professor_id=pid, course_id=cid, text=f"Insight {i}")

    recent = temp_db.get_recent_insights(limit=3)
    assert len(recent) == 3