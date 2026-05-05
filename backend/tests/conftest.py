"""
Pytest fixtures for Atrium.

Provides a fresh, isolated SQLite database for each test, so tests never
interfere with each other or with the live development database.
"""

import pytest
from pathlib import Path

from backend import db


@pytest.fixture
def temp_db(tmp_path):
    """
    Create a fresh, schema-loaded test database in a temporary directory.

    `tmp_path` is a pytest built-in fixture that gives us a unique temp
    directory per test, automatically cleaned up after the test runs.

    Yields the db module itself so tests can call db.create_professor(...)
    etc. without worrying about which database they're hitting.
    """
    test_db_path = tmp_path / "test_atrium.db"
    db.set_db_path(test_db_path)
    db.init_db()

    yield db

    db.reset_db_path()