"""
Tag routes blueprint for task_manager_07

This module handles all tag-related API operations:
- GET /tags - List all tags
- GET /tags/<id> - Get tag details with associated tasks
- POST /tags - Create a new tag
- PUT /tags/<id> - Update an existing tag
- DELETE /tags/<id> - Delete a tag

Demonstrates:
- Simple CRUD operations via a JSON API
- Many-to-many relationships from the "other side"
  (tags can see their tasks via get_tasks(), tasks can see their tags via get_tags())
- Checking for duplicate names before insert/update
- Proper HTTP status codes (200, 201, 400, 404, 409)

Peewee Patterns Demonstrated:
- Querying with ORDER BY for alphabetical sorting
- Using get_or_none() to check if a value exists
- Many-to-many relationship navigation (tag.get_tasks())
- Handling unique constraints
"""

from flask import Blueprint, jsonify, request

from ..models import Tag, TaskTag

# Create blueprint with URL prefix /tags
tags_bp = Blueprint("tags", __name__, url_prefix="/tags")


@tags_bp.route("/", methods=["GET"])
def tags():
    """
    List all tags

    Returns all tags sorted alphabetically with a count
    of associated tasks for each tag.

    Route: GET /tags

    Returns:
        Response: JSON array of tag objects with task_count (200)
    """
    all_tags = Tag.select().order_by(Tag.name)
    result = []
    for tag in all_tags:
        result.append({
            "id": tag.id,
            "name": tag.name,
            "task_count": tag.get_tasks().count(),
        })
    return jsonify(result)


@tags_bp.route("/<int:tag_id>", methods=["GET"])
def tag_detail(tag_id):
    """
    Get tag details with associated tasks

    Route: GET /tags/<tag_id>

    Args:
        tag_id (int): The ID of the tag to display

    Returns:
        dict: Tag data with associated tasks (200) or error (404)
    """
    tag = Tag.get_or_none(Tag.id == tag_id)

    if tag is None:
        return {"error": f"Tag {tag_id} not found"}, 404

    return {
        "id": tag.id,
        "name": tag.name,
        "tasks": [task.to_dict() for task in tag.get_tasks()],
    }


@tags_bp.route("/", methods=["POST"])
def create_tag():
    """
    Create a new tag

    Route: POST /tags

    Expects JSON body:
        {"name": "string"}

    Tag names must be unique.

    Returns:
        dict: Created tag data (201) or error message (400, 409)
    """
    data = request.get_json()

    if not data:
        return {"error": "Request body must be JSON"}, 400

    name = data.get("name")

    if not name:
        return {"error": "Tag name is required"}, 400

    # Check for duplicate tag name
    if Tag.get_or_none(Tag.name == name) is not None:
        return {"error": "Tag name already exists"}, 409

    new_tag = Tag.create(name=name)

    return {"id": new_tag.id, "name": new_tag.name}, 201


@tags_bp.route("/<int:tag_id>", methods=["PUT"])
def edit_tag(tag_id):
    """
    Update an existing tag

    Route: PUT /tags/<tag_id>

    Expects JSON body:
        {"name": "string"}

    Returns:
        dict: Updated tag data (200) or error message (400, 404, 409)
    """
    tag = Tag.get_or_none(Tag.id == tag_id)

    if tag is None:
        return {"error": f"Tag {tag_id} not found"}, 404

    data = request.get_json()

    if not data:
        return {"error": "Request body must be JSON"}, 400

    new_name = data.get("name")

    if not new_name:
        return {"error": "Tag name is required"}, 400

    # Check for duplicate name (only if changed)
    if new_name != tag.name:
        if Tag.get_or_none(Tag.name == new_name) is not None:
            return {"error": "Tag name already exists"}, 409

    tag.name = new_name
    tag.save()

    return {"id": tag.id, "name": tag.name}


@tags_bp.route("/<int:tag_id>", methods=["DELETE"])
def delete_tag(tag_id):
    """
    Delete a tag

    Route: DELETE /tags/<tag_id>

    Cascade behavior: deleting a tag removes task_tag junction records
    but does NOT delete the tasks themselves - just the association.

    Returns:
        dict: Success message (200) or error (404)
    """
    tag = Tag.get_or_none(Tag.id == tag_id)

    if tag is None:
        return {"error": f"Tag {tag_id} not found"}, 404

    name = tag.name
    tag.delete_instance(recursive=True)

    return {"message": f"Tag '{name}' deleted successfully"}
