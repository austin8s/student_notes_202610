"""
Task Manager 06 TUI Client

A read-only Textual TUI with tabbed views for users, tasks, and tags.
Builds on client_05 by adding:
- TabbedContent with multiple DataTables (Users, Tasks, Tags)
- Task filtering (All / Pending / Completed) via key bindings
- Displaying relational data (assignee names, tag lists)

This client is read-only because task_manager_06 only has GET endpoints.

Demonstrates:
- Using TabbedContent and TabPane for multi-view layouts
- Managing multiple DataTable widgets
- Key bindings for filtering data
- Displaying data from a relational database with relationships

Usage:
    First start the API server:
        uv run python run_06.py

    Then in another terminal:
        uv run python run_client_06.py
"""

import httpx
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Footer, Header, Static, TabbedContent, TabPane

from .api import TaskManagerAPI

# ── Default API base URL ────────────────────────────────────────
API_URL = "http://localhost:8080"


class TaskManagerApp(App):
    """
    Read-only TUI for Task Manager 06

    Displays three tabs (Users, Tasks, Tags) with DataTables.
    Tasks can be filtered by status (all, pending, completed).

    Compared to client_05:
    - NEW: Tabbed interface with Users, Tasks, Tags views
    - NEW: Task filtering with 'a' (all), 'p' (pending), 'f' (completed) keys
    - NEW: Multiple DataTables managed independently

    Key Bindings:
        r - Refresh the active tab
        a - Show all tasks (Tasks tab)
        p - Show pending tasks only (Tasks tab)
        f - Show completed (finished) tasks only (Tasks tab)
        q - Quit the application
    """

    TITLE = "Task Manager 06"

    BINDINGS = [
        Binding("r", "refresh", "Refresh", show=True),
        Binding("a", "all_tasks", "All Tasks", show=True),
        Binding("p", "pending_tasks", "Pending", show=True),
        Binding("f", "finished_tasks", "Completed", show=True),
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
            api_url: Base URL of the task_manager_06 API server.
        """
        super().__init__()
        self.api = TaskManagerAPI(api_url)

    def compose(self) -> ComposeResult:
        """Build the UI layout with tabbed DataTables.

        TabbedContent creates a tab bar with switchable panes.
        Each TabPane contains a DataTable for its resource type.

        Yields:
            Widget: UI widgets in display order.
        """
        yield Header()
        with TabbedContent("Users", "Tasks", "Tags"):
            with TabPane("Users", id="users-tab"):
                yield DataTable(id="users-table")
            with TabPane("Tasks", id="tasks-tab"):
                yield DataTable(id="tasks-table")
            with TabPane("Tags", id="tags-tab"):
                yield DataTable(id="tags-table")
        yield Static("Ready", id="status")
        yield Footer()

    def on_mount(self) -> None:
        """Set up table columns and load initial data."""
        # Users table
        users_table = self.query_one("#users-table", DataTable)
        users_table.add_columns("ID", "Username", "Email", "Tasks")
        users_table.cursor_type = "row"

        # Tasks table
        tasks_table = self.query_one("#tasks-table", DataTable)
        tasks_table.add_columns("ID", "Title", "Assignee", "Done", "Tags")
        tasks_table.cursor_type = "row"

        # Tags table
        tags_table = self.query_one("#tags-table", DataTable)
        tags_table.add_columns("ID", "Name", "Tasks")
        tags_table.cursor_type = "row"

        # Load all data
        self.load_users()
        self.load_tasks()
        self.load_tags()

    # ── Data Loading ────────────────────────────────────────────

    def load_users(self) -> None:
        """Fetch users from API and populate the users table."""
        try:
            users = self.api.get_users()
        except httpx.ConnectError:
            self._set_status("Error: Cannot connect to API server")
            return
        except httpx.HTTPStatusError as e:
            self._set_status(f"Error: {e.response.status_code}")
            return

        table = self.query_one("#users-table", DataTable)
        table.clear()
        for user in users:
            table.add_row(
                str(user["id"]),
                user["username"],
                user["email"],
                str(user["task_count"]),
                key=str(user["id"]),
            )
        self._set_status(f"Loaded {len(users)} users")

    def load_tasks(self, filter_type: str = "all") -> None:
        """Fetch tasks from API with optional filtering.

        Args:
            filter_type: One of ``"all"``, ``"pending"``, or ``"completed"``.
        """
        try:
            if filter_type == "pending":
                tasks = self.api.get_pending_tasks()
            elif filter_type == "completed":
                tasks = self.api.get_completed_tasks()
            else:
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
            table.add_row(
                str(task["id"]),
                task["title"],
                task.get("assignee", ""),
                "Yes" if task["is_done"] else "No",
                ", ".join(task.get("tags", [])),
                key=str(task["id"]),
            )
        label = {"all": "all", "pending": "pending", "completed": "completed"}
        self._set_status(f"Loaded {len(tasks)} {label.get(filter_type, '')} tasks")

    def load_tags(self) -> None:
        """Fetch tags from API and populate the tags table."""
        try:
            tags = self.api.get_tags()
        except httpx.ConnectError:
            self._set_status("Error: Cannot connect to API server")
            return
        except httpx.HTTPStatusError as e:
            self._set_status(f"Error: {e.response.status_code}")
            return

        table = self.query_one("#tags-table", DataTable)
        table.clear()
        for tag in tags:
            table.add_row(
                str(tag["id"]),
                tag["name"],
                str(tag["task_count"]),
                key=str(tag["id"]),
            )
        self._set_status(f"Loaded {len(tags)} tags")

    # ── Helpers ─────────────────────────────────────────────────

    def _set_status(self, message: str) -> None:
        """Update the status bar text.

        Args:
            message: Text to display in the status bar.
        """
        self.query_one("#status", Static).update(message)

    def _get_active_tab(self) -> str:
        """Return which tab is currently active.

        Returns:
            str: One of ``"users"``, ``"tasks"``, or ``"tags"``.
        """
        tabbed = self.query_one(TabbedContent)
        active = tabbed.active
        if "users" in active:
            return "users"
        elif "tasks" in active:
            return "tasks"
        return "tags"

    # ── Actions ─────────────────────────────────────────────────

    def action_refresh(self) -> None:
        """Refresh data for the active tab."""
        tab = self._get_active_tab()
        if tab == "users":
            self.load_users()
        elif tab == "tasks":
            self.load_tasks()
        else:
            self.load_tags()

    def action_all_tasks(self) -> None:
        """Show all tasks (switches to Tasks tab)."""
        self.load_tasks("all")

    def action_pending_tasks(self) -> None:
        """Show only pending tasks."""
        self.load_tasks("pending")

    def action_finished_tasks(self) -> None:
        """Show only completed tasks."""
        self.load_tasks("completed")
        self.load_tasks("completed")
        self.load_tasks("completed")
        self.load_tasks("completed")
