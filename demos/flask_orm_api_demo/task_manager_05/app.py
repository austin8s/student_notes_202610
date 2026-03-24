"""
task_manager_05 - Task manager JSON API with Peewee ORM
This demonstrates how to use SQLite database with Peewee ORM
and serve the data through a JSON API
"""

from pathlib import Path

from flask import Flask

from . import tasks
from .database import db


def create_app():
    """
    Application factory function.

    Creates and configures the Flask application with Peewee ORM,
    including database initialization and request hooks.

    Returns:
        Flask: Configured Flask application with database and blueprints.
    """
    app = Flask(__name__)

    # Get grandparent directory of this file
    parent_dir = Path(__file__).resolve().parent.parent

    # Ensure the instance directory exists
    (parent_dir / "instance").mkdir(exist_ok=True)

    # Initialize Peewee database with the SQLite file path
    # Unlike Flask-SQLAlchemy, Peewee uses db.init() to set the database path
    # The database file will be stored at: /project/instance/tasks_05.db
    db.init(str(parent_dir / "instance" / "tasks_05.db"))

    # Register Flask hooks for database connection management
    # Peewee requires explicit connection open/close per request
    @app.before_request
    def before_request():
        """Open a database connection before each request."""
        db.connect(reuse_if_open=True)

    @app.teardown_appcontext
    def teardown(exc):
        """Close the database connection after each request.

        Args:
            exc: Exception raised during the request, or None.
        """
        if not db.is_closed():
            db.close()

    # Register the tasks blueprint
    app.register_blueprint(tasks.blue_print)

    return app
