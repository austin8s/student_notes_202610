"""Application configuration.

Stores settings as simple module-level variables.  The application
factory reads these when it starts up.  In tests you can use
``monkeypatch`` to override any value before calling ``create_app()``.
"""

from pathlib import Path

DATABASE_PATH = str(Path(__file__).resolve().parent.parent / "instance" / "books.db")
"""str: Absolute path to the SQLite database file."""
