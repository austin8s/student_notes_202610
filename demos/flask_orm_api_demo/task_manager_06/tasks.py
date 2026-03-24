"""
Task views for task_manager_06
Handles all task-related API routes (read-only)

This module demonstrates:
- Querying Task model with various Peewee methods
- Filtering tasks (pending, completed) using .where() clauses
- Navigating many-to-one relationship (Task → User via ForeignKeyField)
- Navigating many-to-many relationship (Task ↔ Tags via TaskTag through-model)
- Returning related data in JSON responses
"""

from flask import Blueprint, jsonify

from .models import Task

# Tasks blueprint with URL prefix /tasks
# All routes in this blueprint will start with /tasks
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("/")
def list_tasks():
    """
    List all tasks with assignees and tags as JSON

    Demonstrates:
    - Basic query for all tasks using Task.select()
    - Converting ORM objects to dicts with relationship data
    - task.to_dict() includes assignee name and tag names

    Returns:
        Response: JSON array of task objects with nested relationship data
    """
    tasks = Task.select()
    return jsonify([task.to_dict() for task in tasks])


@tasks_bp.route("/<int:task_id>")
def task_detail(task_id):
    """
    Get task details with assignee and tags

    Demonstrates:
    - Query by primary key using get_or_none()
    - Navigating to related user (task.assignee)
    - Navigating to related tags (task.get_tags())

    Args:
        task_id: Primary key of the task to display

    Returns:
        dict: JSON response with task details (200) or error (404)
    """
    task = Task.get_or_none(Task.id == task_id)

    if task is None:
        return {"error": f"Task {task_id} not found"}, 404

    return task.to_dict()


@tasks_bp.route("/pending")
def pending_tasks():
    """
    List only pending (not completed) tasks

    Demonstrates:
    - Filtering with .where() clause
    - Using boolean filters (is_done == False)

    Returns:
        Response: JSON array of pending task objects
    """
    tasks = Task.select().where(Task.is_done)
    return jsonify([task.to_dict() for task in tasks])


@tasks_bp.route("/completed")
def completed_tasks():
    """
    List only completed tasks

    Demonstrates:
    - Filtering with WHERE clause for True values

    Returns:
        Response: JSON array of completed task objects
    """
    tasks = Task.select().where(Task.is_done)
    return jsonify([task.to_dict() for task in tasks])
