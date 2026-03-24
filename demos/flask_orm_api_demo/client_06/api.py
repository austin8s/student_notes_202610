"""
API Client for Task Manager 06

Extends the client_05 API client with support for multiple resources:
users, tasks (with filtering), and tags.

Compared to client_05:
- NEW: User endpoints (list, detail)
- NEW: Task filtering endpoints (pending, completed)
- NEW: Tag endpoints (list, detail)
- NEW: Stats endpoint with database counts

This client is still read-only (GET requests only) because
task_manager_06 does not support write operations.

Demonstrates:
- Expanding an API client to cover multiple resource endpoints
- Using the same httpx pattern for different URL paths
- Read-only API consumption

Usage:
    api = TaskManagerAPI("http://localhost:8080")
    users = api.get_users()
    pending = api.get_pending_tasks()
    tags = api.get_tags()
"""

import httpx


class TaskManagerAPI:
    """
    Client for the Task Manager 06 REST API (read-only)

    Supports reading users, tasks (with filtering), and tags.
    task_manager_06 has a relational schema with User, Task, Tag,
    and TaskTag tables, but only exposes GET endpoints.

    Attributes:
        base_url (str): The base URL of the API server
        client (httpx.Client): The httpx client instance
    """

    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.client = httpx.Client(
            base_url=base_url, timeout=10.0, follow_redirects=True
        )

    # ── Stats ───────────────────────────────────────────────────

    def get_stats(self):
        """Get API statistics including user, task, and tag counts.

        Returns:
            dict: API metadata with nested ``stats`` object.
        """
        response = self.client.get("/")
        response.raise_for_status()
        return response.json()

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
        """Get user details with their tasks.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            dict: User data including nested task list.
        """
        response = self.client.get(f"/users/{user_id}")
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

    def get_pending_tasks(self):
        """List only pending (incomplete) tasks.

        Returns:
            list[dict]: Pending task objects.
        """
        response = self.client.get("/tasks/pending")
        response.raise_for_status()
        return response.json()

    def get_completed_tasks(self):
        """List only completed tasks.

        Returns:
            list[dict]: Completed task objects.
        """
        response = self.client.get("/tasks/completed")
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
