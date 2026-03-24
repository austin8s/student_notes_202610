"""
API Client for the Task Manager

This module provides a Python class that wraps all HTTP calls
to the Task Manager 07 REST API using the httpx library.

Demonstrates:
- Encapsulating API calls in a reusable class
- Making GET, POST, PUT, DELETE requests with httpx
- Sending and receiving JSON data
- Handling HTTP errors

Usage:
    api = TaskManagerAPI("http://localhost:8080")
    users = api.get_users()
    new_user = api.create_user("Smith, John", "john@example.com")
"""

import httpx


class TaskManagerAPI:
    """
    Client for the Task Manager REST API

    Wraps httpx HTTP calls to provide a clean Python interface
    for all CRUD operations on users, tasks, and tags.

    Attributes:
        base_url (str): The base URL of the API server
        client (httpx.Client): The httpx client instance

    Example:
        api = TaskManagerAPI("http://localhost:8080")
        users = api.get_users()     # GET /users/
        user = api.get_user(1)      # GET /users/1
    """

    def __init__(self, base_url="http://localhost:8080"):
        """
        Initialize the API client

        Args:
            base_url: The base URL of the Task Manager API server
        """
        self.base_url = base_url
        self.client = httpx.Client(
            base_url=base_url, timeout=10.0, follow_redirects=True
        )

    # ── User endpoints ──────────────────────────────────────────

    def get_users(self):
        """List all users.

        Returns:
            list[dict]: User objects with task counts.
        """
        response = self.client.get("/users/")
        response.raise_for_status()
        return response.json()

    def get_user(self, user_id):
        """Get user details including their tasks.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            dict: User data with nested active and completed task lists.
        """
        response = self.client.get(f"/users/{user_id}")
        response.raise_for_status()
        return response.json()

    def create_user(self, username, email):
        """Create a new user.

        Args:
            username: Display name in ``"Lastname, Firstname"`` format.
            email: Email address (must be unique).

        Returns:
            dict: The newly created user data.
        """
        response = self.client.post(
            "/users/", json={"username": username, "email": email}
        )
        response.raise_for_status()
        return response.json()

    def update_user(self, user_id, username, email):
        """Update an existing user.

        Args:
            user_id: The ID of the user to update.
            username: New username.
            email: New email address.

        Returns:
            dict: The updated user data.
        """
        response = self.client.put(
            f"/users/{user_id}", json={"username": username, "email": email}
        )
        response.raise_for_status()
        return response.json()

    def delete_user(self, user_id):
        """Delete a user and their tasks.

        Args:
            user_id: The ID of the user to delete.

        Returns:
            dict: Confirmation message.
        """
        response = self.client.delete(f"/users/{user_id}")
        response.raise_for_status()
        return response.json()

    # ── Task endpoints ──────────────────────────────────────────

    def get_tasks(self):
        """List all tasks.

        Returns:
            list[dict]: Task objects with assignee and tag data.
        """
        response = self.client.get("/tasks/")
        response.raise_for_status()
        return response.json()

    def get_task(self, task_id):
        """Get details for a single task.

        Args:
            task_id: The ID of the task to retrieve.

        Returns:
            dict: Task data with assignee and tags.
        """
        response = self.client.get(f"/tasks/{task_id}")
        response.raise_for_status()
        return response.json()

    def create_task(self, title, assignee_id, details="", tag_ids=None):
        """Create a new task.

        Args:
            title: Short description of the task.
            assignee_id: ID of the user to assign the task to.
            details: Full task description (optional).
            tag_ids: List of tag IDs to associate (optional).

        Returns:
            dict: The newly created task data.
        """
        payload = {
            "title": title,
            "details": details,
            "assignee_id": assignee_id,
            "tag_ids": tag_ids or [],
        }
        response = self.client.post("/tasks/", json=payload)
        response.raise_for_status()
        return response.json()

    def update_task(
        self, task_id, title, assignee_id, details="", is_done=False, tag_ids=None
    ):
        """Update an existing task.

        Args:
            task_id: The ID of the task to update.
            title: New task title.
            assignee_id: New assignee user ID.
            details: New task details.
            is_done: New completion status.
            tag_ids: New list of tag IDs (replaces existing).

        Returns:
            dict: The updated task data.
        """
        payload = {
            "title": title,
            "details": details,
            "assignee_id": assignee_id,
            "is_done": is_done,
            "tag_ids": tag_ids or [],
        }
        response = self.client.put(f"/tasks/{task_id}", json=payload)
        response.raise_for_status()
        return response.json()

    def toggle_task(self, task_id):
        """Toggle a task's completion status.

        Args:
            task_id: The ID of the task to toggle.

        Returns:
            dict: The updated task data.
        """
        response = self.client.post(f"/tasks/{task_id}/toggle")
        response.raise_for_status()
        return response.json()

    def delete_task(self, task_id):
        """Delete a task.

        Args:
            task_id: The ID of the task to delete.

        Returns:
            dict: Confirmation message.
        """
        response = self.client.delete(f"/tasks/{task_id}")
        response.raise_for_status()
        return response.json()

    # ── Tag endpoints ───────────────────────────────────────────

    def get_tags(self):
        """List all tags with task counts.

        Returns:
            list[dict]: Tag objects with ``task_count``.
        """
        response = self.client.get("/tags/")
        response.raise_for_status()
        return response.json()

    def get_tag(self, tag_id):
        """Get tag details with associated tasks.

        Args:
            tag_id: The ID of the tag to retrieve.

        Returns:
            dict: Tag data with nested task list.
        """
        response = self.client.get(f"/tags/{tag_id}")
        response.raise_for_status()
        return response.json()

    def create_tag(self, name):
        """Create a new tag.

        Args:
            name: Tag name (must be unique).

        Returns:
            dict: The newly created tag data.
        """
        response = self.client.post("/tags/", json={"name": name})
        response.raise_for_status()
        return response.json()

    def update_tag(self, tag_id, name):
        """Update an existing tag.

        Args:
            tag_id: The ID of the tag to update.
            name: New tag name.

        Returns:
            dict: The updated tag data.
        """
        response = self.client.put(f"/tags/{tag_id}", json={"name": name})
        response.raise_for_status()
        return response.json()

    def delete_tag(self, tag_id):
        """Delete a tag.

        Args:
            tag_id: The ID of the tag to delete.

        Returns:
            dict: Confirmation message.
        """
        response = self.client.delete(f"/tags/{tag_id}")
        response.raise_for_status()
        return response.json()

    # ── Stats ───────────────────────────────────────────────────

    def get_stats(self):
        """Get API statistics including user, task, and tag counts.

        Returns:
            dict: API metadata with nested ``stats`` object.
        """
        response = self.client.get("/")
        response.raise_for_status()
        return response.json()
