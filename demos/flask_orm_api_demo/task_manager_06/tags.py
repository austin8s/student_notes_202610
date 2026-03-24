"""
Tag views for task_manager_06
Handles all tag-related API routes (read-only)

Demonstrates:
- Querying Tag model with Peewee methods
- Navigating many-to-many relationship (Tag ↔ Tasks via TaskTag through-model)
- Including related task data in JSON responses
"""

from flask import Blueprint, jsonify

from .models import Tag

# Tags blueprint with URL prefix
tags_bp = Blueprint("tags", __name__, url_prefix="/tags")


@tags_bp.route("/")
def list_tags():
    """
    List all tags with task counts

    Returns:
        Response: JSON array of tag objects
    """
    tags = Tag.select()
    result = []
    for tag in tags:
        result.append(
            {
                "id": tag.id,
                "name": tag.name,
                "task_count": tag.get_tasks().count(),
            }
        )
    return jsonify(result)


@tags_bp.route("/<int:tag_id>")
def tag_detail(tag_id):
    """
    Get tag details and associated tasks

    Args:
        tag_id: Primary key of the tag to display

    Returns:
        dict: JSON response with tag details and associated tasks (200) or error (404)
    """
    tag = Tag.get_or_none(Tag.id == tag_id)

    if tag is None:
        return {"error": f"Tag {tag_id} not found"}, 404

    return {
        "id": tag.id,
        "name": tag.name,
        "tasks": [task.to_dict() for task in tag.get_tasks()],
    }
