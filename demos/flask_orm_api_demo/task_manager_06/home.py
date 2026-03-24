"""
Home views for task_manager_06
Returns API information and status as JSON
"""

from flask import Blueprint
from peewee import fn

from .models import Tag, Task, User

# Main blueprint
home_bp = Blueprint("main", __name__)


@home_bp.route("/")
def home():
    """
    API root - returns status and statistics.

    Provides an overview of the API including:
    - Available endpoints
    - Database statistics (user, task, tag counts)

    Returns:
        dict: JSON response with API metadata and database statistics.
    """
    return {
        "message": "Task Manager 06 API",
        "version": "0.6.0",
        "stats": {
            "users": User.select(fn.COUNT(User.id)).scalar(),
            "tasks": Task.select(fn.COUNT(Task.id)).scalar(),
            "tags": Tag.select(fn.COUNT(Tag.id)).scalar(),
        },
        "endpoints": {
            "users": "/users",
            "tasks": "/tasks",
            "tags": "/tags",
        },
    }
