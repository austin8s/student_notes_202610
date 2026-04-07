"""Book application package.

Provides the ``create_app`` application factory that configures the
Flask app, sets up the SQLite database, and registers blueprints.

The *application factory* is a common Flask pattern where a function
(rather than module-level code) builds and returns the app object.
This makes testing easier and avoids circular-import problems.
"""

from pathlib import Path

from flask import Flask

from . import config
from .database import db
from .models import Book


def create_app():
    """Application factory — creates and configures the Flask app.

    This function follows the *application factory* pattern recommended
    by Flask.  It performs three setup steps:

    1. **Database** — reads the path from ``config.DATABASE_PATH``,
       ensures the parent directory exists, and registers
       before/after-request hooks to open and close connections
       automatically.
    2. **Blueprints** — registers the ``api`` blueprint so the route
       handlers in ``book_app.api.routes`` become active.
    3. **Tables** — calls ``create_tables`` with ``safe=True`` so
       Peewee creates any missing tables on the first run without
       raising an error on subsequent runs.

    Returns:
        flask.Flask: The fully configured Flask application instance.
    """
    app = Flask(__name__)

    # --- Database setup ---
    # The path comes from config.py — tests can monkeypatch it.
    db_path = Path(config.DATABASE_PATH)
    db_path.parent.mkdir(exist_ok=True)
    db.init(str(db_path))

    # Open a connection before each request
    @app.before_request
    def before_request():
        db.connect(reuse_if_open=True)

    # Close the connection after each request (even on error)
    @app.teardown_appcontext
    def teardown(exc):
        if not db.is_closed():
            db.close()

    # --- Blueprint registration ---
    from .api import api_bp

    app.register_blueprint(api_bp)

    # --- Table creation ---
    # safe=True → creates the table on the first run, does nothing after that
    db.connect(reuse_if_open=True)
    db.create_tables([Book], safe=True)
    db.close()

    return app
