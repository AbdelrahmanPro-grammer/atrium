"""
Atrium — Seed script.

Populates the database with realistic fictional data for development and demos.

Course codes and titles are based on the public Qatar University CS curriculum,
so course information feels authentic. Professor names and all insight text are
entirely fictional and were written for demonstration purposes only.

Usage:
    python scripts/seed.py
"""

import sys
from pathlib import Path

# Make the backend package importable when running this script directly.
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend import db


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

PROFESSORS = [
    ("Dr. Ahmed Al-Mansouri",  "Computer Science"),
    ("Dr. Sara Khalid",        "Computer Science"),
    ("Dr. David Chen",         "Computer Science"),
    ("Dr. Omar Sharif",        "Computer Science"),
    ("Dr. Mohammed Hassan",    "Mathematics"),
    ("Dr. Noor Abdulla",       "Mathematics"),
    ("Dr. Fatima Al-Sayed",    "Statistics"),
    ("Dr. Layla Othman",       "Physics"),
    ("Dr. James Patterson",    "English"),
    ("Dr. Yusuf Rahman",       "Arabic"),
]

COURSES = [
    ("CMPS 151", "Programming Concepts"),
    ("CMPS 251", "Object-Oriented Programming"),
    ("CMPS 303", "Data Structures"),
    ("CMPS 323", "Design and Analysis of Algorithms"),
    ("CMPS 351", "Fundamentals of Database Systems"),
    ("CMPS 350", "Web Development Fundamentals"),
    ("CMPS 310", "Software Engineering"),
    ("CMPS 405", "Operating Systems"),
    ("CMPS 380", "Cybersecurity Fundamentals"),
    ("CMPS 403", "Artificial Intelligence"),
    ("CMPS 460", "Machine Learning"),
    ("MATH 101", "Calculus I"),
    ("MATH 231", "Linear Algebra"),
    ("PHYS 191", "General Physics for Engineering I"),
    ("ENGL 202", "English Language I Post Foundation"),
]

# Insights are tuples of:
#   (professor_index, course_index, text, workload, clarity, fairness)
# Indexes refer to the lists above (0-based). Some have no ratings — that's
# intentional, since ratings are optional in the schema.
INSIGHTS = [
    (0, 0, "Lectures move quickly but the slides are well organized. Practice problems on your own; the labs alone aren't enough.", "moderate", 4, 4),
    (0, 0, "Office hours are genuinely useful. Bring specific questions, not vague ones.", None, 5, None),
    (0, 1, "Project-based grading. Start your assignments early — partial credit is generous if you submit something working.", "heavy", 4, 5),

    (1, 2, "Strong foundation in data structures. Quizzes are short but require careful reading. Don't skim the textbook chapters.", "moderate", 5, 4),
    (1, 4, "Database concepts are taught with real SQL exercises in class. The midterm is fair if you've done the homework.", "moderate", 5, 5),
    (1, 2, "She explains pointer-based structures more clearly than any tutorial I've found online.", None, 5, None),

    (2, 3, "Algorithms course is conceptually heavy. Make sure you can derive complexities, not just memorize them.", "heavy", 4, 4),
    (2, 7, "Operating systems with hands-on assignments in C. The xv6 project is the highlight of the semester.", "heavy", 5, 4),

    (3, 6, "Software engineering taught with a real team project. You'll learn Git workflows the hard way — embrace it.", "moderate", 4, 5),
    (3, 5, "Web development fundamentals — covers HTML, CSS, JavaScript, and a bit of backend. Good for beginners.", "light", 4, 5),
    (3, 6, "Grading rubrics are clear and posted in advance. Communicate early if your team has issues.", None, None, 5),

    (4, 11, "Calculus taught traditionally. Lots of practice problems. The pace is steady, not rushed.", "moderate", 4, 5),
    (4, 11, "Bring questions to office hours — they're rarely crowded and very productive.", None, 5, None),

    (5, 12, "Linear algebra with strong emphasis on geometric intuition, not just matrix manipulation.", "moderate", 5, 5),
    (5, 12, "Proofs are introduced gradually. If you've never written one, you'll be fine here.", "light", 4, None),

    (6, 10, "Machine learning with real Python notebooks. The professor focuses on understanding over plug-and-play.", "heavy", 5, 4),
    (6, 10, "Final project is open-ended. Pick something you actually care about — it makes the work easier.", None, 4, 5),

    (7, 13, "Physics with engineering applications. The labs are demanding but well structured.", "heavy", 4, 4),
    (7, 13, "Concept questions on exams test understanding, not formula recall. Study the conceptual chapters carefully.", "moderate", 5, 5),

    (8, 14, "Writing-intensive course. Drafts and peer reviews matter as much as the final essay.", "moderate", 4, 5),
    (8, 14, "Feedback on drafts is detailed and genuinely helpful. Take it seriously.", None, 5, None),

    (9, 8, "Cybersecurity fundamentals. Hands-on labs are the best part — set aside time for them.", "moderate", 4, 4),

    (0, 0, "If you're new to programming, this is a forgiving introduction. Don't compare yourself to classmates with prior experience.", None, None, None),
    (1, 4, "Bring a laptop to class — there are live SQL demos most weeks.", None, None, None),
    (2, 3, "Read the textbook before lecture. The class makes more sense that way.", None, None, None),
    (3, 5, "Final project can be in any framework. Pick one you want to learn, not one that seems easy.", None, None, None),
    (4, 11, "Practice problems are graded for effort, not correctness. Always submit them.", None, None, None),
    (6, 10, "Office hours fill up before exams — go early in the semester to build a rapport.", None, None, None),
    (8, 14, "The reading load is real. Don't fall behind in the first three weeks.", None, None, None),
    (5, 12, "Linear algebra connects to a lot of later CS courses. Worth investing extra time.", None, None, None),
]


# ---------------------------------------------------------------------------
# Seeding logic
# ---------------------------------------------------------------------------

def seed() -> None:
    """Initialize the schema and populate with seed data."""
    print("Initializing database...")
    db.init_db()

    print("Inserting professors...")
    professor_ids = [
        db.create_professor(name, dept) for name, dept in PROFESSORS
    ]

    print("Inserting courses...")
    course_ids = [
        db.create_course(code, name) for code, name in COURSES
    ]

    print("Inserting insights...")
    for prof_idx, course_idx, text, workload, clarity, fairness in INSIGHTS:
        db.create_insight(
            professor_id=professor_ids[prof_idx],
            course_id=course_ids[course_idx],
            text=text,
            workload=workload,
            clarity=clarity,
            fairness=fairness,
        )

    print()
    print(f"  {len(professor_ids)} professors")
    print(f"  {len(course_ids)} courses")
    print(f"  {len(INSIGHTS)} insights")
    print()
    print("Seeding complete.")


if __name__ == "__main__":
    seed()