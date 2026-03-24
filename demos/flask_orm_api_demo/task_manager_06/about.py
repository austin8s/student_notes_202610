"""
About views for task_manager_06
Returns application information as JSON
"""

from flask import Blueprint

# About blueprint
about_bp = Blueprint("about", __name__)


@about_bp.route("/about")
def about():
    """
    About endpoint.

    Returns information about the application,
    database schema, and relationships as JSON.

    Returns:
        dict: JSON response with application metadata and schema description.
    """
    return {
        "name": "Task Manager",
        "description": "A task management API with relational database",
        "version": "0.6.0",
        "schema": {
            "users": "User table with username, email, created_at",
            "tasks": "Task table with title, details, is_done, assignee (FK to user)",
            "tags": "Tag table with name",
            "task_tags": "Junction table linking tasks and tags (many-to-many)",
        },
    }
