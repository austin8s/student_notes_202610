"""
User routes blueprint for task_manager_07

This module handles all user-related API operations:
- GET /users - List all users
- GET /users/<id> - Get user details with their tasks
- POST /users - Create a new user
- PUT /users/<id> - Update an existing user
- DELETE /users/<id> - Delete a user

Demonstrates:
- CRUD operations via a JSON API
- Using request.get_json() to parse JSON request bodies
- Input validation with JSON error responses
- Proper HTTP status codes (200, 201, 400, 404, 409)
"""

from flask import Blueprint, jsonify, request

from ..models import Task, User

# Create a blueprint for user-related routes
users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/", methods=["GET"])
def users():
    """
    List all users

    Route: GET /users

    Returns:
        Response: JSON array of user objects (200)
    """
    all_users = User.select().order_by(User.username)
    return jsonify([user.to_dict() for user in all_users])


@users_bp.route("/<int:user_id>", methods=["GET"])
def user_detail(user_id):
    """
    Get user details and their tasks

    Route: GET /users/<user_id>

    Args:
        user_id (int): The ID of the user to display

    Returns:
        dict: JSON response with user details and tasks (200) or error (404)
    """
    user = User.get_or_none(User.id == user_id)

    if user is None:
        return {"error": f"User {user_id} not found"}, 404

    # Build response with user details and categorized tasks
    user_data = user.to_dict()
    user_data["active_tasks"] = [
        task.to_dict()
        for task in Task.select().where(
            (Task.assignee == user_id) & (Task.is_done == False)
        )
    ]
    user_data["completed_tasks"] = [
        task.to_dict()
        for task in Task.select().where(
            (Task.assignee == user_id) & (Task.is_done == True)
        )
    ]

    return user_data


@users_bp.route("/", methods=["POST"])
def create_user():
    """
    Create a new user

    Route: POST /users

    Expects JSON body:
        {"username": "string", "email": "string"}

    request.get_json() parses the JSON body from the HTTP request.
    The client must send Content-Type: application/json header.

    Returns:
        dict: Created user data (201) or error message (400, 409)
    """
    # Parse JSON from request body
    # request.get_json() returns None if the body isn't valid JSON
    data = request.get_json()

    if not data:
        return {"error": "Request body must be JSON"}, 400

    username = data.get("username")
    email = data.get("email")

    # Validate required fields
    if not username or not email:
        return {"error": "Username and email are required"}, 400

    # Check for duplicate username
    if User.get_or_none(User.username == username) is not None:
        return {"error": "Username already exists"}, 409

    # Check for duplicate email
    if User.get_or_none(User.email == email) is not None:
        return {"error": "Email already exists"}, 409

    # Create new user - Model.create() inserts and returns the instance
    new_user = User.create(username=username, email=email)

    # Return 201 Created with the new user data
    return new_user.to_dict(), 201


@users_bp.route("/<int:user_id>", methods=["PUT"])
def edit_user(user_id):
    """
    Update an existing user

    Route: PUT /users/<user_id>

    Expects JSON body:
        {"username": "string", "email": "string"}

    Returns:
        dict: Updated user data (200) or error message (400, 404, 409)
    """
    user = User.get_or_none(User.id == user_id)

    if user is None:
        return {"error": f"User {user_id} not found"}, 404

    data = request.get_json()

    if not data:
        return {"error": "Request body must be JSON"}, 400

    new_username = data.get("username")
    new_email = data.get("email")

    if not new_username or not new_email:
        return {"error": "Username and email are required"}, 400

    # Check for duplicate username (only if changed)
    if new_username != user.username:
        if User.get_or_none(User.username == new_username) is not None:
            return {"error": "Username already exists"}, 409

    # Check for duplicate email (only if changed)
    if new_email != user.email:
        if User.get_or_none(User.email == new_email) is not None:
            return {"error": "Email already exists"}, 409

    # Update and save
    user.username = new_username
    user.email = new_email
    user.save()

    return user.to_dict()


@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    Delete a user

    Route: DELETE /users/<user_id>

    Cascade behavior: deleting a user also deletes their tasks
    and associated task_tag records (via ON DELETE CASCADE).

    Returns:
        dict: Success message (200) or error (404)
    """
    user = User.get_or_none(User.id == user_id)

    if user is None:
        return {"error": f"User {user_id} not found"}, 404

    username = user.username
    user.delete_instance(recursive=True)

    return {"message": f"User '{username}' deleted successfully"}
