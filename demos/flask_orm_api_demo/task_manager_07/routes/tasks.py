"""
Task routes blueprint for task_manager_07

This module handles all task-related API operations:
- GET /tasks - List all tasks
- GET /tasks/<id> - Get task details with tags and assignee
- POST /tasks - Create a new task (with tags)
- PUT /tasks/<id> - Update an existing task (with tags)
- POST /tasks/<id>/toggle - Toggle task completion status
- DELETE /tasks/<id> - Delete a task

Demonstrates:
- CRUD operations via a JSON API
- Many-to-many relationships (tasks and tags) via TaskTag through-model
- Using request.get_json() to parse JSON request bodies
- Proper HTTP status codes (200, 201, 400, 404)

Peewee Query Patterns Used:
- Model.select().order_by() - Get sorted records
- Model.get_or_none() - Get single record safely
- Model.create() - Create and save a new record
- model.save() - Save changes to existing record
- model.delete_instance() - Delete a single record
- TaskTag through-model for many-to-many management
"""

from flask import Blueprint, jsonify, request

from ..models import Tag, Task, TaskTag, User

# Create blueprint with URL prefix /tasks
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("/", methods=["GET"])
def tasks():
    """
    List all tasks

    Returns all tasks sorted by completion status and title.
    Incomplete tasks appear first, then completed tasks.

    Route: GET /tasks

    Returns:
        Response: JSON array of task objects (200)
    """
    all_tasks = Task.select().order_by(Task.is_done, Task.title)
    return jsonify([task.to_dict() for task in all_tasks])


@tasks_bp.route("/<int:task_id>", methods=["GET"])
def task_detail(task_id):
    """
    Get task details

    Returns full information about a specific task including
    assigned user and associated tags.

    Route: GET /tasks/<task_id>

    Args:
        task_id (int): The ID of the task to display

    Returns:
        dict: Task data with tags and assignee (200) or error (404)
    """
    task = Task.get_or_none(Task.id == task_id)

    if task is None:
        return {"error": f"Task {task_id} not found"}, 404

    return task.to_dict()


@tasks_bp.route("/", methods=["POST"])
def create_task():
    """
    Create a new task

    Route: POST /tasks

    Expects JSON body:
        {
            "title": "string",
            "details": "string" (optional),
            "assignee_id": int,
            "tag_ids": [int, ...] (optional)
        }

    Many-to-Many with Peewee:
    When creating a task with tags:
    1. Create the Task record first
    2. For each tag_id, create a TaskTag record
    3. TaskTag links the task and tag via foreign keys

    Returns:
        dict: Created task data (201) or error message (400)
    """
    data = request.get_json()

    if not data:
        return {"error": "Request body must be JSON"}, 400

    title = data.get("title")
    details = data.get("details", "")
    assignee_id = data.get("assignee_id")
    tag_ids = data.get("tag_ids", [])

    # Validate required fields
    if not title or not assignee_id:
        return {"error": "Title and assignee_id are required"}, 400

    # Verify the assignee exists
    if User.get_or_none(User.id == assignee_id) is None:
        return {"error": f"User {assignee_id} not found"}, 404

    # Create the task
    new_task = Task.create(
        title=title,
        details=details,
        assignee=assignee_id,
    )

    # Create many-to-many relationships via TaskTag through-model
    for tag_id in tag_ids:
        if Tag.get_or_none(Tag.id == tag_id) is not None:
            TaskTag.create(task=new_task, tag=tag_id)

    return new_task.to_dict(), 201


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
def edit_task(task_id):
    """
    Update an existing task

    Route: PUT /tasks/<task_id>

    Expects JSON body:
        {
            "title": "string",
            "details": "string",
            "assignee_id": int,
            "is_done": bool,
            "tag_ids": [int, ...]
        }

    Updating Many-to-Many Relationships in Peewee:
    1. Delete all existing TaskTag records for this task
    2. Create new TaskTag records for the selected tags
    This "delete all, re-insert" pattern is simple and reliable.

    Returns:
        dict: Updated task data (200) or error message (400, 404)
    """
    task = Task.get_or_none(Task.id == task_id)

    if task is None:
        return {"error": f"Task {task_id} not found"}, 404

    data = request.get_json()

    if not data:
        return {"error": "Request body must be JSON"}, 400

    title = data.get("title")
    assignee_id = data.get("assignee_id")

    if not title or not assignee_id:
        return {"error": "Title and assignee_id are required"}, 400

    # Verify the assignee exists
    if User.get_or_none(User.id == assignee_id) is None:
        return {"error": f"User {assignee_id} not found"}, 404

    # Update task fields
    task.title = title
    task.details = data.get("details", "")
    task.is_done = data.get("is_done", task.is_done)
    task.assignee = assignee_id
    task.save()

    # Update many-to-many: delete all existing, re-insert selected
    TaskTag.delete().where(TaskTag.task == task).execute()

    tag_ids = data.get("tag_ids", [])
    for tag_id in tag_ids:
        if Tag.get_or_none(Tag.id == tag_id) is not None:
            TaskTag.create(task=task, tag=tag_id)

    return task.to_dict()


@tasks_bp.route("/<int:task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    """
    Toggle task completion status

    Switches a task between complete and incomplete.

    Route: POST /tasks/<task_id>/toggle

    Args:
        task_id (int): ID of the task to toggle

    Returns:
        dict: Updated task data (200) or error (404)
    """
    task = Task.get_or_none(Task.id == task_id)

    if task is None:
        return {"error": f"Task {task_id} not found"}, 404

    task.is_done = not task.is_done
    task.save()

    return task.to_dict()


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """
    Delete a task

    Route: DELETE /tasks/<task_id>

    Cascade behavior: deleting a task also deletes associated
    task_tag junction records (via ON DELETE CASCADE).

    Returns:
        dict: Success message (200) or error (404)
    """
    task = Task.get_or_none(Task.id == task_id)

    if task is None:
        return {"error": f"Task {task_id} not found"}, 404

    title = task.title
    task.delete_instance(recursive=True)

    return {"message": f"Task '{title}' deleted successfully"}
