"""
task_manager_06 - Task manager JSON API with relational database design
This demonstrates a normalized database schema with multiple tables and relationships
served through a RESTful JSON API

Key concepts demonstrated in this application:
- Multiple related tables (Users, Tasks, Tags)
- Foreign key relationships (Task → User)
- Many-to-many relationships (Tasks ↔ Tags) via junction/through model
- Peewee ForeignKeyField for easy navigation between related objects
- Modular view organization (separate files per resource)
- JSON API responses with nested relationship data

Application Architecture:
- app.py: Main application setup and configuration
- database.py: Database instance (db) configuration
- models.py: ORM models (User, Task, Tag, TaskTag)
- home.py, users.py, tasks.py, tags.py: Route blueprints returning JSON
"""

from pathlib import Path

from flask import Flask

from .database import db
from .home import home_bp
from .tags import tags_bp
from .tasks import tasks_bp
from .users import users_bp


def create_app():
    """
    Application factory function
    Creates and configures the Flask application with Peewee

    Returns:
        Flask: Configured Flask application with database and blueprints
    """
    # Create the Flask application instance
    app = Flask(__name__)

    # Get grandparent directory of this file
    parent_dir = Path(__file__).resolve().parent.parent

    # Initialize Peewee database with the SQLite file path
    db.init(str(parent_dir / "instance" / "tasks_06.db"))

    # Register Flask hooks for database connection management
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

    # Register all blueprints (route modules)
    app.register_blueprint(home_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(tags_bp)

    # Return the fully configured Flask application
    return app
