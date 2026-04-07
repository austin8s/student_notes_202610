"""API route handlers for CRUD operations on books.

CRUD stands for **C**reate, **R**ead, **U**pdate, **D**elete — the
four basic operations for persistent storage.  Each function below
handles one HTTP method/path combination and uses Peewee ORM calls
instead of raw SQL.
"""

from flask import current_app, jsonify, request

from ..models import Book
from . import api_bp


@api_bp.route("/books", methods=["GET"])
def list_books():
    """Return all books, sorted by title.

    Peewee's ``select()`` is equivalent to ``SELECT * FROM book``.
    Chaining ``order_by()`` adds an ``ORDER BY`` clause.

    Returns:
        flask.Response: JSON array of book objects with HTTP 200.
    """
    books = Book.select().order_by(Book.title)
    # jsonify() is needed here because we are returning a list, not a dict
    return jsonify([book.to_dict() for book in books])


@api_bp.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    """Return a single book by its primary key.

    ``get_or_none`` returns ``None`` instead of raising a
    ``DoesNotExist`` exception when the ID is not found.

    Args:
        book_id (int): Primary key of the book to retrieve.

    Returns:
        tuple | dict: The book as a dict (HTTP 200), or an error
        dict with HTTP 404 if not found.
    """
    book = Book.get_or_none(Book.id == book_id)

    if book is None:
        return {"error": f"Book {book_id} not found"}, 404

    return book.to_dict()


@api_bp.route("/books", methods=["POST"])
def create_book():
    """Create a new book from a JSON request body.

    Expects a JSON object with at least ``title`` and ``author``.
    Peewee's ``Model.create()`` inserts a new row and returns the
    model instance with its auto-generated ``id``.

    Returns:
        tuple: The newly created book as a dict with HTTP 201,
        or an error dict with HTTP 400 if validation fails.
    """
    data = request.get_json()

    if not data:
        return {"error": "Request body must be JSON"}, 400

    title = data.get("title")
    author = data.get("author")

    if not title or not author:
        return {"error": "title and author are required"}, 400

    book = Book.create(title=title, author=author)
    return book.to_dict(), 201


@api_bp.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    """Update an existing book's fields.

    Accepts a JSON body with any combination of ``title``, ``author``,
    and ``is_read``.  Fields not included in the request body keep
    their current values.  ``model.save()`` issues an ``UPDATE``
    statement for the row.

    Args:
        book_id (int): Primary key of the book to update.

    Returns:
        tuple | dict: The updated book as a dict (HTTP 200), or an
        error dict with HTTP 404 / 400.
    """
    book = Book.get_or_none(Book.id == book_id)

    if book is None:
        return {"error": f"Book {book_id} not found"}, 404

    data = request.get_json()

    if not data:
        return {"error": "Request body must be JSON"}, 400

    book.title = data.get("title", book.title)
    book.author = data.get("author", book.author)
    book.is_read = data.get("is_read", book.is_read)
    book.save()

    return book.to_dict()


@api_bp.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    """Delete a book by its primary key.

    ``delete_instance()`` issues a ``DELETE FROM book WHERE id = ?``
    statement for the single row.

    Args:
        book_id (int): Primary key of the book to delete.

    Returns:
        tuple | dict: A confirmation message (HTTP 200), or an error
        dict with HTTP 404 if the book does not exist.
    """
    book = Book.get_or_none(Book.id == book_id)

    if book is None:
        return {"error": f"Book {book_id} not found"}, 404

    title = book.title
    book.delete_instance()

    return {"message": f"'{title}' deleted"}
