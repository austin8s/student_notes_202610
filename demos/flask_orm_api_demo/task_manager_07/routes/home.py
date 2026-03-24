"""
Home route for task_manager_07

Returns API status and statistics as JSON.
Demonstrates aggregate queries with Peewee fn.COUNT().
"""

from flask import Blueprint
from peewee import fn

from ..models import Tag, Task, User

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home():
    """
    API root - returns status and database statistics

    Uses Peewee aggregate queries:
    - fn.COUNT() creates SQL COUNT() function
    - .scalar() returns the single count value

    Returns:
        dict: JSON response with API info and database statistics
    """
    total_users = User.select(fn.COUNT(User.id)).scalar()
    total_tags = Tag.select(fn.COUNT(Tag.id)).scalar()
    total_tasks = Task.select(fn.COUNT(Task.id)).scalar()
    completed_tasks = Task.select(fn.COUNT(Task.id)).where(Task.is_done).scalar()
    pending_tasks = total_tasks - completed_tasks

    return {
        "message": "Task Manager 07 API",
        "version": "0.7.0",
        "stats": {
            "users": total_users,
            "tasks": total_tasks,
            "tags": total_tags,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
        },
        "endpoints": {
            "users": "/users",
            "tasks": "/tasks",
            "tags": "/tags",
        },
    }
