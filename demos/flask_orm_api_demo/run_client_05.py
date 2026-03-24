"""
Entry script for the Task Manager 05 TUI Client

Starts the simple read-only Textual terminal UI that connects
to the Task Manager 05 API running on localhost:8080.

Usage:
    First start the API server:
        uv run python run_05.py

    Then in another terminal:
        uv run python run_client_05.py
"""

from client_05.app import TaskManagerApp

app = TaskManagerApp()

if __name__ == "__main__":
    app.run()
