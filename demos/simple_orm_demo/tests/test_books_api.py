"""Tests for the /api/books endpoints.

Each test receives a ``client`` fixture (defined in conftest.py) that
provides a Flask test client backed by a temporary database pre-loaded
with three sample books.  No real server is started — Flask processes
the request in-process.

Run the tests with::

    uv run pytest
"""

from tests.conftest import SEED_BOOKS

# ---------------------------------------------------------------------------
# GET /api/books
# ---------------------------------------------------------------------------


def test_list_books_returns_seed_data(client):
    """The list endpoint should return all seed books."""
    response = client.get("/api/books")

    assert response.status_code == 200

    books = response.get_json()
    assert len(books) == len(SEED_BOOKS)


def test_list_books_sorted_by_title(client):
    """Books should be returned in alphabetical order by title."""
    titles = [b["title"] for b in client.get("/api/books").get_json()]

    assert titles == sorted(titles)


def test_list_books_after_create(client):
    """Creating a new book should increase the total count by one."""
    client.post("/api/books", json={"title": "New Book", "author": "Author"})

    books = client.get("/api/books").get_json()

    assert len(books) == len(SEED_BOOKS) + 1


# ---------------------------------------------------------------------------
# POST /api/books
# ---------------------------------------------------------------------------


def test_create_book(client):
    """POST with valid JSON should return the new book with HTTP 201."""
    response = client.post(
        "/api/books",
        json={"title": "Clean Code", "author": "Robert C. Martin"},
    )

    assert response.status_code == 201

    data = response.get_json()
    assert data["title"] == "Clean Code"
    assert data["author"] == "Robert C. Martin"
    assert data["is_read"] is False
    assert "id" in data


def test_create_book_missing_fields(client):
    """POST without both title and author should return HTTP 400."""
    response = client.post("/api/books", json={"title": "No Author"})

    assert response.status_code == 400
    assert "required" in response.get_json()["error"]


def test_create_book_no_json_body(client):
    """POST with a non-JSON body should not return a success status."""
    response = client.post(
        "/api/books",
        data="not json",
        content_type="application/json",
    )

    assert response.status_code == 400


# ---------------------------------------------------------------------------
# GET /api/books/<id>
# ---------------------------------------------------------------------------


def test_get_book(client):
    """GET with a valid id should return that single book."""
    response = client.get("/api/books/1")

    assert response.status_code == 200
    assert response.get_json()["title"] == "Design Patterns"


def test_get_book_not_found(client):
    """GET with a non-existent id should return HTTP 404."""
    response = client.get("/api/books/999")

    assert response.status_code == 404
    assert "not found" in response.get_json()["error"]


# ---------------------------------------------------------------------------
# PUT /api/books/<id>
# ---------------------------------------------------------------------------


def test_update_book(client):
    """PUT should update only the fields included in the request."""
    response = client.put(
        "/api/books/1",
        json={"title": "New Title", "is_read": True},
    )

    assert response.status_code == 200

    data = response.get_json()
    assert data["title"] == "New Title"
    assert data["author"] == "Gang of Four"  # unchanged
    assert data["is_read"] is True


def test_update_book_not_found(client):
    """PUT on a non-existent id should return HTTP 404."""
    response = client.put(
        "/api/books/999",
        json={"title": "Doesn't Matter"},
    )

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/books/<id>
# ---------------------------------------------------------------------------


def test_delete_book(client):
    """DELETE should remove the book and return a confirmation message."""
    response = client.delete("/api/books/1")

    assert response.status_code == 200
    assert "deleted" in response.get_json()["message"]

    # Confirm the book is actually gone
    assert client.get("/api/books/1").status_code == 404

    # Confirm total count decreased
    books = client.get("/api/books").get_json()
    assert len(books) == len(SEED_BOOKS) - 1


def test_delete_book_not_found(client):
    """DELETE on a non-existent id should return HTTP 404."""
    response = client.delete("/api/books/999")

    assert response.status_code == 404
