"""
task_manager_03 - Task manager JSON API with structured responses
This demonstrates returning structured JSON responses with proper HTTP status codes

Key concepts introduced:
- Returning dictionaries (Flask auto-serializes to JSON)
- Using jsonify() for lists (required since Flask only auto-serializes dicts)
- HTTP status codes (200, 404) as second return value
- Consistent JSON response structure
"""

from flask import Flask

# Support both running as a package and as a script
try:
    from . import tasks  # type: ignore
except ImportError:
    import tasks  # type: ignore


def create_app():
    """
    Application factory function
    Creates and configures the Flask application

    This version includes:
    - Blueprints for organizing routes
    - Structured JSON responses with status codes
    - Error handling returning JSON

    Returns:
        Flask: Configured Flask application with registered blueprints
    """
    app = Flask(__name__)
    app.register_blueprint(tasks.blue_print)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="localhost", port=8080, debug=True)
