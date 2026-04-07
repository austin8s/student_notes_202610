"""Shared test fixtures.

The ``client`` fixture provides a Flask test client backed by a
temporary database that is pre-loaded with sample books.  Every test
that accepts ``client`` as a parameter gets its own isolated copy —
tests never interfere with each other.

Fixtures:
    client: Test client with three seed books already in the database.

Seed data (inserted in alphabetical order by title):

====  ====================  ====================  =========
 id   title                 author                is_read
====  ====================  ====================  =========
 1    Design Patterns       Gang of Four          False
 2    Pragmatic Programmer  David Thomas          True
 3    Refactoring           Martin Fowler         False
====  ====================  ====================  =========
"""

import pytest

from book_app import config

SEED_BOOKS = [
    {"title": "Design Patterns", "author": "Gang of Four"},
    {"title": "Pragmatic Programmer", "author": "David Thomas", "is_read": True},
    {"title": "Refactoring", "author": "Martin Fowler"},
]
"""list[dict]: Books inserted into the database before each test."""


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Flask test client with seed data in an isolated temporary database.

    ``monkeypatch.setattr`` replaces the ``DATABASE_PATH`` variable in
    ``book_app.config`` so that ``create_app()`` points the database
    at a temporary file.  Three sample books are then inserted via the
    API so every test starts with realistic data.

    Args:
        tmp_path: Built-in pytest fixture that provides a unique
            temporary directory for each test.
        monkeypatch: Built-in pytest fixture that lets you replace
            attributes for the duration of a single test.

    Yields:
        flask.testing.FlaskClient: A client you can use to send
        HTTP requests to the app without starting a real server.
    """
    monkeypatch.setattr(config, "DATABASE_PATH", str(tmp_path / "test.db"))

    from book_app import create_app

    app = create_app()

    with app.test_client() as test_client:
        for book in SEED_BOOKS:
            test_client.post("/api/books", json=book)

        yield test_client
