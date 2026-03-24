"""
Task Manager 05 TUI Client

A simple Textual TUI that displays tasks from the task_manager_05 API.
This is the most basic TUI client - a single read-only DataTable
showing all tasks from a single-table database.

Demonstrates:
- Building a minimal Textual application
- Using a DataTable widget to display API data
- Connecting a TUI to a REST API via the api.py client class

Usage:
    First start the API server:
        uv run python run_05.py

    Then in another terminal:
        uv run python run_client_05.py
"""

import httpx
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Footer, Header, Static

from .api import TaskManagerAPI

# ── Default API base URL ────────────────────────────────────────
API_URL = "http://localhost:8080"


class TaskManagerApp(App):
    """
    Simple read-only TUI for Task Manager 05

    Displays a single table of tasks fetched from the API.
    This is the simplest possible Textual app - just a DataTable
    with a refresh key binding.

    Key Bindings:
        r - Refresh the task list
        q - Quit the application
    """

    TITLE = "Task Manager 05"

    BINDINGS = [
        Binding("r", "refresh", "Refresh", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    CSS = """
    #status {
        dock: bottom;
        height: 1;
        background: $accent;
        color: $text;
        padding: 0 1;
    }
    DataTable {
        height: 1fr;
    }
    """

    def __init__(self, api_url: str = API_URL) -> None:
        """Initialize the TUI application.

        Args:
            api_url: Base URL of the task_manager_05 API server.
        """
        super().__init__()
        self.api = TaskManagerAPI(api_url)

    def compose(self) -> ComposeResult:
        """Build the UI layout.

        A simple layout with just a header, data table, status bar,
        and footer showing key bindings.

        Yields:
            Widget: UI widgets in display order.
        """
        yield Header()
        yield DataTable(id="tasks-table")
        yield Static("Ready", id="status")
        yield Footer()

    def on_mount(self) -> None:
        """Set up DataTable columns and load initial data.

        Called when the app is first mounted.
        """
        table = self.query_one("#tasks-table", DataTable)
        table.add_columns("ID", "Title", "Assignee", "Done", "Tags")
        table.cursor_type = "row"
        self.load_tasks()

    def load_tasks(self) -> None:
        """Fetch tasks from the API and populate the table.

        Clears existing rows and reloads all tasks. Updates the
        status bar with the result count or an error message.
        """
        try:
            tasks = self.api.get_tasks()
        except httpx.ConnectError:
            self._set_status("Error: Cannot connect to API server")
            return
        except httpx.HTTPStatusError as e:
            self._set_status(f"Error: {e.response.status_code}")
            return

        table = self.query_one("#tasks-table", DataTable)
        table.clear()
        for task in tasks:
            # task_manager_05 Task.to_dict() has: id, title, details,
            # is_done, assignee, tags (JSON string field)
            tags = task.get("tags", "")
            if isinstance(tags, list):
                tags = ", ".join(tags)
            table.add_row(
                str(task["id"]),
                task["title"],
                task.get("assignee", ""),
                "Yes" if task["is_done"] else "No",
                tags,
                key=str(task["id"]),
            )
        self._set_status(f"Loaded {len(tasks)} tasks")

    def _set_status(self, message: str) -> None:
        """Update the status bar text.

        Args:
            message: Text to display in the status bar.
        """
        self.query_one("#status", Static).update(message)

    def action_refresh(self) -> None:
        """Refresh the task list from the API."""
        self.load_tasks()
