"""
Echo Server — A practice API for learning httpx

This server manages a simple inventory of items. It validates all
incoming requests and returns detailed feedback in every response,
including an "echo" object that shows exactly what the server received.

Run with:
    uv run python server.py

Endpoints:
    GET    /api/status          — Server health check
    GET    /api/items           — List all items
    GET    /api/items/<id>      — Get one item by ID
    POST   /api/items           — Create a new item (requires JSON with "name")
    PUT    /api/items/<id>      — Update an existing item
    DELETE /api/items/<id>      — Delete an item
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

# ── In-memory data store — pre-seeded with sample items ─────────
items = [
    {"id": 1, "name": "Temperature Sensor", "category": "sensor", "value": 22.5},
    {"id": 2, "name": "Pressure Gauge", "category": "sensor", "value": 101.3},
    {"id": 3, "name": "LED Indicator", "category": "output", "value": 1},
]
next_id = 4


# ── Health check ────────────────────────────────────────────────
@app.route("/api/status")
def status():
    """Return server health check information.

    Returns:
        dict: JSON with server status, item count, and a welcome message.
    """
    return {
        "status": "online",
        "item_count": len(items),
        "message": "Echo server is running. Send requests to /api/items",
    }


# ── READ ────────────────────────────────────────────────────────
@app.route("/api/items", methods=["GET"])
def list_items():
    """Return all items in the inventory.

    Returns:
        flask.Response: JSON array of all item objects.
    """
    return jsonify(items)


@app.route("/api/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Return a single item by its ID.

    Args:
        item_id: The integer ID of the item to retrieve.

    Returns:
        dict: The item object if found (200), or an error message (404).
    """
    for item in items:
        if item["id"] == item_id:
            return item
    return {"error": f"Item {item_id} not found"}, 404


# ── CREATE ──────────────────────────────────────────────────────
@app.route("/api/items", methods=["POST"])
def create_item():
    """Create a new item in the inventory.

    Expects a JSON body with at least a ``name`` field. Optional fields
    are ``category`` (defaults to ``"general"``) and ``value`` (defaults
    to ``0``).

    Returns:
        tuple: A JSON object with a success message, the created item, and
            an echo of the received request (201). Returns an error with a
            hint on 400 if the body is missing or invalid.
    """
    global next_id
    data = request.get_json()

    if data is None:
        return {
            "error": "Request body must be JSON",
            "hint": "Use httpx.post(url, json={...}) — the json= parameter "
            "sets the Content-Type header and encodes the body for you",
        }, 400

    if "name" not in data:
        return {
            "error": "Missing required field: name",
            "hint": 'Send JSON with at least a "name" field, '
            'e.g. json={"name": "My Item"}',
        }, 400

    new_item = {
        "id": next_id,
        "name": data["name"],
        "category": data.get("category", "general"),
        "value": data.get("value", 0),
    }
    next_id += 1
    items.append(new_item)

    return {
        "message": f"Item '{new_item['name']}' created successfully",
        "item": new_item,
        "echo": {
            "method": "POST",
            "url": "/api/items",
            "body_received": data,
        },
    }, 201


# ── UPDATE ──────────────────────────────────────────────────────
@app.route("/api/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    """Update an existing item's fields.

    Accepts a JSON body with any combination of ``name``, ``category``,
    and ``value``. Only the provided fields are updated.

    Args:
        item_id: The integer ID of the item to update.

    Returns:
        dict: A JSON object with a success message, the updated item, and
            an echo of the received request (200). Returns 404 if the item
            does not exist, or 400 if the body is not valid JSON.
    """
    data = request.get_json()

    if data is None:
        return {
            "error": "Request body must be JSON",
            "hint": "Use httpx.put(url, json={...}) — the json= parameter "
            "sets the Content-Type header and encodes the body for you",
        }, 400

    for item in items:
        if item["id"] == item_id:
            if "name" in data:
                item["name"] = data["name"]
            if "category" in data:
                item["category"] = data["category"]
            if "value" in data:
                item["value"] = data["value"]

            return {
                "message": f"Item {item_id} updated successfully",
                "item": item,
                "echo": {
                    "method": "PUT",
                    "url": f"/api/items/{item_id}",
                    "body_received": data,
                },
            }

    return {"error": f"Item {item_id} not found"}, 404


# ── DELETE ──────────────────────────────────────────────────────
@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """Delete an item from the inventory.

    Args:
        item_id: The integer ID of the item to delete.

    Returns:
        dict: A JSON object with a success message, the deleted item, and
            an echo of the received request (200). Returns 404 if the item
            does not exist.
    """
    for i, item in enumerate(items):
        if item["id"] == item_id:
            deleted = items.pop(i)
            return {
                "message": f"Item '{deleted['name']}' deleted successfully",
                "deleted_item": deleted,
                "echo": {
                    "method": "DELETE",
                    "url": f"/api/items/{item_id}",
                },
            }

    return {"error": f"Item {item_id} not found"}, 404


# ── Startup ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Echo Server — Practice API for httpx exercises")
    print("  Endpoints:")
    print("    GET    http://localhost:5000/api/status")
    print("    GET    http://localhost:5000/api/items")
    print("    GET    http://localhost:5000/api/items/<id>")
    print("    POST   http://localhost:5000/api/items")
    print("    PUT    http://localhost:5000/api/items/<id>")
    print("    DELETE http://localhost:5000/api/items/<id>")
    print("=" * 60)
    app.run(host="localhost", port=5000, debug=True)
