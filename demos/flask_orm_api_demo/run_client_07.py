"""
Entry script for the Task Manager 07 TUI Client

Starts the full CRUD Textual terminal UI that connects to the
Task Manager 07 API running on localhost:8080.

Usage:
    First start the API server:
        uv run python run_07.py

    Then in another terminal:
        uv run python run_client_07.py
"""

from client_07.app import TaskManagerApp

app = TaskManagerApp()

if __name__ == "__main__":
    app.run()
