"""
Atrium — Flask API.

The HTTP layer. Every route here translates an HTTP request into a call
to the data access layer (db.py) and returns a JSON response.

Endpoints:
    GET  /api/health                       — service health check
    GET  /api/professors                   — list all professors
    GET  /api/professors/<id>              — single professor with their insights
    GET  /api/courses                      — list all courses
    GET  /api/insights                     — recent insights across all professors
    POST /api/insights                     — submit a new insight
    POST /api/insights/<id>/helpful        — mark an insight as helpful
"""

from flask import Flask, jsonify, request, abort
from flask_cors import CORS

from backend import db


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = Flask(__name__)

# CORS allows the frontend (served from a different origin during development)
# to call this API. In production we'd restrict this to known origins.
CORS(app)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    """Quick check that the service is up. Useful for CI and debugging."""
    return jsonify({"status": "ok", "service": "atrium"})


# ---------------------------------------------------------------------------
# Professors
# ---------------------------------------------------------------------------

@app.route("/api/professors", methods=["GET"])
def list_professors():
    """Return all professors, sorted by name."""
    return jsonify(db.get_all_professors())


@app.route("/api/professors/<int:professor_id>", methods=["GET"])
def get_professor_detail(professor_id):
    """
    Return a single professor along with all their insights.
    Returns 404 if the professor does not exist.
    """
    professor = db.get_professor(professor_id)
    if professor is None:
        abort(404, description="Professor not found")

    insights = db.get_insights_for_professor(professor_id)
    return jsonify({
        "professor": professor,
        "insights": insights,
    })


# ---------------------------------------------------------------------------
# Courses
# ---------------------------------------------------------------------------

@app.route("/api/courses", methods=["GET"])
def list_courses():
    """Return all courses, sorted by code."""
    return jsonify(db.get_all_courses())


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

@app.route("/api/insights", methods=["GET"])
def list_recent_insights():
    """Return the most recent insights across all professors."""
    # Optional ?limit=N query parameter, defaulting to 20, capped at 100.
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        abort(400, description="limit must be an integer")
    limit = max(1, min(limit, 100))

    return jsonify(db.get_recent_insights(limit=limit))


@app.route("/api/insights", methods=["POST"])
def create_insight():
    """
    Submit a new insight.

    Required JSON fields:
        professor_id (int)
        course_id    (int)
        text         (str, non-empty after stripping)

    Optional JSON fields:
        workload  (str: 'light' | 'moderate' | 'heavy')
        clarity   (int: 1..5)
        fairness  (int: 1..5)
    """
    data = request.get_json(silent=True) or {}

    # Required fields
    professor_id = data.get("professor_id")
    course_id = data.get("course_id")
    text = (data.get("text") or "").strip()

    if not isinstance(professor_id, int):
        abort(400, description="professor_id is required and must be an integer")
    if not isinstance(course_id, int):
        abort(400, description="course_id is required and must be an integer")
    if not text:
        abort(400, description="text is required and cannot be empty")
    if len(text) > 2000:
        abort(400, description="text must be 2000 characters or fewer")

    # Validate the referenced professor exists. Better error than a foreign-key
    # exception bubbling up from SQLite.
    if db.get_professor(professor_id) is None:
        abort(404, description="Professor not found")

    # Optional fields — validate only if present.
    workload = data.get("workload")
    if workload is not None and workload not in ("light", "moderate", "heavy"):
        abort(400, description="workload must be 'light', 'moderate', or 'heavy'")

    clarity = data.get("clarity")
    if clarity is not None and (not isinstance(clarity, int) or not 1 <= clarity <= 5):
        abort(400, description="clarity must be an integer between 1 and 5")

    fairness = data.get("fairness")
    if fairness is not None and (not isinstance(fairness, int) or not 1 <= fairness <= 5):
        abort(400, description="fairness must be an integer between 1 and 5")

    new_id = db.create_insight(
        professor_id=professor_id,
        course_id=course_id,
        text=text,
        workload=workload,
        clarity=clarity,
        fairness=fairness,
    )

    return jsonify({"id": new_id, "status": "created"}), 201


@app.route("/api/insights/<int:insight_id>/helpful", methods=["POST"])
def mark_helpful(insight_id):
    """Increment the helpful count on an insight."""
    if not db.increment_helpful_count(insight_id):
        abort(404, description="Insight not found")
    return jsonify({"id": insight_id, "status": "marked helpful"})


# ---------------------------------------------------------------------------
# Error handlers — return JSON instead of HTML for API errors
# ---------------------------------------------------------------------------

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "bad_request", "message": str(error.description)}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "not_found", "message": str(error.description)}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "method_not_allowed", "message": str(error.description)}), 405


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)