"""
User views for task_manager_06
Handles all user-related API routes (read-only)

Demonstrates:
- Querying User model with Peewee
- Navigating one-to-many relationships (User → Tasks via backref)
- Returning related data in JSON responses
"""

from flask import Blueprint, jsonify

from .models import User

# User blueprint with URL prefix
users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/")
def list_users():
    """
    List all users with task counts

    Demonstrates:
    - Basic query for all users
    - Converting ORM objects to dicts for JSON serialization
    - Including relationship counts in the response

    Returns:
        Response: JSON array of user objects
    """
    users = User.select()
    return jsonify([user.to_dict() for user in users])


@users_bp.route("/<int:user_id>")
def user_detail(user_id):
    """
    Get user details and their tasks

    Demonstrates:
    - Query by primary key using get_or_none
    - Navigating one-to-many relationship (user.tasks via backref)
    - Including nested task data in the JSON response

    Args:
        user_id: Primary key of the user to display

    Returns:
        dict: JSON response with user details and tasks (200) or error (404)
    """
    user = User.get_or_none(User.id == user_id)

    if user is None:
        return {"error": f"User {user_id} not found"}, 404

    # Build response with user details and their tasks
    user_data = user.to_dict()
    user_data["tasks"] = [task.to_dict() for task in user.tasks]

    return user_data
