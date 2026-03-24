"""
API Client for Task Manager 05

A minimal API client that wraps HTTP calls to the task_manager_05 API.
This is the simplest client - it only supports reading tasks from a
single-table database.

Demonstrates:
- Creating an API client class with httpx
- Making GET requests and parsing JSON responses
- Basic error handling with raise_for_status()

Usage:
    api = TaskManagerAPI("http://localhost:8080")
    tasks = api.get_tasks()
    task = api.get_task(1)
"""

import httpx


class TaskManagerAPI:
    """
    Client for the Task Manager 05 REST API (read-only)

    This is the simplest API client - only GET requests for tasks.
    task_manager_05 has a single Task table with no relationships.

    Attributes:
        base_url (str): The base URL of the API server
        client (httpx.Client): The httpx client instance
    """

    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.client = httpx.Client(
            base_url=base_url, timeout=10.0, follow_redirects=True
        )

    def get_info(self):
        """Get API metadata.

        Returns:
            dict: API information including version and endpoints.
        """
        response = self.client.get("/")
        response.raise_for_status()
        return response.json()

    def get_tasks(self):
        """List all tasks.

        Returns:
            list[dict]: List of task dictionaries.
        """
        response = self.client.get("/tasks")
        response.raise_for_status()
        return response.json()

    def get_task(self, task_id):
        """Get details for a single task.

        Args:
            task_id: The ID of the task to retrieve.

        Returns:
            dict: Task data including title, assignee, and tags.
        """
        response = self.client.get(f"/tasks/{task_id}")
        response.raise_for_status()
        return response.json()
