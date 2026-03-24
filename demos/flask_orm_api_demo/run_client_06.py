"""
Entry script for the Task Manager 06 TUI Client

Starts the read-only multi-table Textual terminal UI that connects
to the Task Manager 06 API running on localhost:8080.

Usage:
    First start the API server:
        uv run python run_06.py

    Then in another terminal:
        uv run python run_client_06.py
"""

from client_06.app import TaskManagerApp

app = TaskManagerApp()

if __name__ == "__main__":
    app.run()
