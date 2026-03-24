"""
Tasks blueprint for task_manager_05
Contains route definitions that query the database using Peewee ORM
and return JSON responses

This demonstrates:
- Querying database using Peewee ORM
- Using Model.select() to retrieve all records
- Using Model.get_or_none() to retrieve a single record
- Converting ORM objects to dictionaries for JSON serialization
- Returning JSON responses from database-backed API endpoints
"""

from flask import Blueprint, jsonify

from .models import Task

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
        "message": "Task Manager 05 API",
        "version": "0.5.0",
        "endpoints": ["/", "/about", "/tasks", "/tasks/<id>"],
    }


@blue_print.route("/about")
def about():
    """
    About endpoint

    Returns:
        dict: JSON response with app description
    """
    return {
        "name": "Task Manager",
        "description": "A task management API with Peewee ORM and SQLite",
        "version": "0.5.0",
    }


@blue_print.route("/tasks")
def task_list():
    """
    List all tasks from the database

    This function:
    1. Queries all tasks from the database using Peewee ORM
    2. Converts each Task model instance to a dictionary using to_dict()
    3. Returns the list as a JSON array

    Peewee ORM query patterns:
    - Task.select(): Creates a SELECT query for all columns in Task table
    - The result is an iterable of Task model instances

    Returns:
        Response: JSON array of all task objects from the database
    """
    # Query all tasks from the database
    # Task.select() creates: SELECT * FROM task
    # Returns an iterable of Task model instances
    tasks = Task.select()

    # Convert ORM objects to dictionaries for JSON serialization
    # Each Task has a to_dict() method defined in models.py
    return jsonify([task.to_dict() for task in tasks])


@blue_print.route("/tasks/<int:task_id>")
def task_detail(task_id):
    """
    Get a single task by ID from the database

    Demonstrates:
    - Query by primary key using get_or_none()
    - ORM object to dictionary conversion
    - 404 handling for missing records

    Args:
        task_id: The primary key of the task to retrieve

    Returns:
        dict: JSON response with task data (200) or error message (404)
    """
    # Get task by primary key
    # Returns Task object or None
    task = Task.get_or_none(Task.id == task_id)

    if task is None:
        return {"error": f"Task {task_id} not found"}, 404

    return task.to_dict()
