"""
task_manager_07 - Full CRUD JSON API
Extends task_manager_06 with full Create, Read, Update, Delete operations
served through a RESTful JSON API

This is a complete Flask API application demonstrating:
- Application Factory Pattern: A function that creates and configures the app
- Database Integration: Using Peewee ORM for database operations
- Blueprints: Organizing routes into separate modules
- CRUD Operations: Creating, Reading, Updating, and Deleting database records
- JSON request/response: Using request.get_json() for input, returning dicts/lists
- RESTful design: Using HTTP methods (GET, POST, PUT, DELETE) for operations
"""

# Standard library import for working with file system paths
from pathlib import Path

# Flask is the web framework - it handles HTTP requests/responses
from flask import Flask

from .database import db
from .models import Tag, Task, TaskTag, User


def register_blueprints(app):
    """
    Register all blueprints with the Flask application

    Blueprints are like mini-applications that group related routes together.

    In this app, we have 4 blueprints:
    - home_bp: API root with statistics
    - users_bp: All user-related API routes (list, create, update, delete)
    - tasks_bp: All task-related API routes (list, create, update, toggle, delete)
    - tags_bp: All tag-related API routes (list, create, update, delete)

    Args:
        app: The Flask application instance to register blueprints with
    """
    from .routes.home import home_bp
    from .routes.tags import tags_bp
    from .routes.tasks import tasks_bp
    from .routes.users import users_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(tags_bp)


def create_app():
    """
    Application Factory Function

    Returns:
        Flask: A fully configured Flask application instance
    """
    app = Flask(__name__)

    parent_dir = Path(__file__).resolve().parent.parent

    # Ensure the instance directory exists
    (parent_dir / "instance").mkdir(exist_ok=True)

    # Initialize Peewee database with the SQLite file path
    db.init(str(parent_dir / "instance" / "tasks_07.db"))

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

    # Register all blueprints (routes) with the app
    register_blueprints(app)

    # Create database tables if they don't exist
    db.connect(reuse_if_open=True)
    db.create_tables([User, Tag, Task, TaskTag], safe=True)
    db.close()

    return app
