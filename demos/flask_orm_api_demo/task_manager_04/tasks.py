"""
Tasks blueprint for task_manager_04
Contains route definitions that access application data and return JSON responses

This demonstrates:
- Accessing data stored in app.config using current_app
- Returning data as JSON from API endpoints
- Filtering and looking up data from an in-memory list
- Proper HTTP status codes for success (200) and not found (404)
"""

from flask import Blueprint, current_app, jsonify

# Create a blueprint named "tasks"
blue_print = Blueprint("tasks", __name__)


@blue_print.route("/")
def home():
    """
    API root endpoint

    Returns API information and available endpoints

    Returns:
        dict: JSON response with API metadata
    """
    return {
        "message": "Task Manager 04 API",
        "version": "0.4.0",
        "endpoints": ["/", "/about", "/tasks", "/tasks/<id>"],
    }


@blue_print.route("/about")
def about():
    """
    About endpoint

    Returns application metadata as JSON

    Returns:
        dict: JSON response with app description
    """
    return {
        "name": "Task Manager",
        "description": "A task management API with CSV data",
        "version": "0.4.0",
    }


@blue_print.route("/tasks")
def task_list():
    """
    List all tasks endpoint

    This function:
    1. Retrieves task data from app.config (loaded from CSV file)
    2. Returns the data as a JSON array

    current_app is a special Flask object that represents the current application.
    It's used inside view functions to access the application's configuration.

    Returns:
        Response: JSON array of all task objects
    """
    # Access the tasks data from app configuration
    # current_app.config["tasks"] retrieves the data we loaded in create_app()
    # This data was read from tasks.csv when the application started
    tasks_data = current_app.config["tasks"]

    # jsonify() is needed for returning lists as JSON
    # Flask only auto-serializes dicts, not lists
    return jsonify(tasks_data)


@blue_print.route("/tasks/<int:task_id>")
def task_detail(task_id):
    """
    Get a single task by ID

    Demonstrates:
    - Dynamic URL parameters (<int:task_id>)
    - Searching through a list of dictionaries
    - Returning 404 for resources not found

    Args:
        task_id: The ID of the task to retrieve (from URL)

    Returns:
        dict: JSON response with task data (200) or error message (404)
    """
    tasks_data = current_app.config["tasks"]

    # Search for the task with matching ID
    # next() with a generator expression finds the first match or returns None
    task = next((t for t in tasks_data if t["id"] == task_id), None)

    if task is None:
        return {"error": f"Task {task_id} not found"}, 404

    return task
