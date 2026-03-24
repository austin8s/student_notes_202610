"""
Tasks blueprint for task_manager_03
Contains route definitions that return structured JSON responses

Instead of returning plain text or rendering templates, these routes
return Python dictionaries and lists as JSON responses.

Key concepts:
- Flask automatically serializes dictionaries to JSON (Content-Type: application/json)
- For lists, use flask.jsonify() since auto-serialization only works for dicts
- Return a tuple (response, status_code) to set HTTP status codes
- Use consistent response structure for API design
"""

from flask import Blueprint, jsonify

# Create a blueprint named "tasks"
# This blueprint will organize all task-related routes
blue_print = Blueprint("tasks", __name__)


@blue_print.route("/")
def home():
    """
    View function for the API root

    Returns a JSON object with API information.
    Flask automatically converts the returned dictionary to a JSON response
    with Content-Type: application/json header.

    Returns:
        dict: JSON response with API information (HTTP 200 by default)
    """
    # Returning a dict → Flask auto-serializes to JSON
    return {
        "message": "Task Manager 03 API",
        "version": "0.3.0",
        "endpoints": ["/", "/about", "/tasks"],
    }


@blue_print.route("/about")
def about():
    """
    View function for the about endpoint

    Returns application metadata as JSON.

    Returns:
        dict: JSON response with application details
    """
    return {
        "name": "Task Manager",
        "description": "A simple task management API",
        "version": "0.3.0",
    }


@blue_print.route("/tasks")
def task_list():
    """
    View function that returns a list of sample tasks as JSON

    Demonstrates using jsonify() for returning lists.
    Flask only auto-serializes dicts; for lists, you must use jsonify().

    Returns:
        Response: JSON array of task objects
    """
    # Sample static data (will come from CSV/database in later versions)
    tasks = [
        {"id": 1, "title": "Learn Flask", "is_done": False},
        {"id": 2, "title": "Build an API", "is_done": False},
        {"id": 3, "title": "Install Python", "is_done": True},
    ]
    # jsonify() is needed for lists — dicts are auto-serialized but lists are not
    return jsonify(tasks)


@blue_print.route("/tasks/<int:task_id>")
def task_detail(task_id):
    """
    View function for a single task by ID

    Demonstrates:
    - Dynamic URL parameters (<int:task_id>)
    - Returning different HTTP status codes
    - Error responses as JSON (not HTML error pages)

    Args:
        task_id: The ID of the task to retrieve (from URL)

    Returns:
        dict: JSON response with task data (200) or error message (404)
    """
    # Sample static data
    tasks = {
        1: {"id": 1, "title": "Learn Flask", "is_done": False},
        2: {"id": 2, "title": "Build an API", "is_done": False},
        3: {"id": 3, "title": "Install Python", "is_done": True},
    }

    if task_id not in tasks:
        # Return error as JSON with 404 status code
        # The second value in the tuple sets the HTTP status code
        return {"error": f"Task {task_id} not found"}, 404

    return tasks[task_id]
