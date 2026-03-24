"""
Task Manager TUI Client

A Textual-based terminal user interface (TUI) client that connects
to the Task Manager 07 REST API.

Demonstrates:
- Building a terminal UI with Textual (https://textual.textualize.io/)
- Consuming a REST API from a client application
- Separating the API client (api.py) from the UI (this file)
- Using DataTable widgets for tabular data display
- Using Modal screens for create/edit forms
- Key bindings for keyboard-driven interaction

Usage:
    First start the API server:
        uv run python run_07.py

    Then in another terminal:
        uv run python run_client.py
"""

import httpx
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
    TabbedContent,
    TabPane,
)

from .api import TaskManagerAPI

# ── Default API base URL ────────────────────────────────────────
API_URL = "http://localhost:8080"


# ═══════════════════════════════════════════════════════════════
# Modal Screens for Create/Edit Forms
# ═══════════════════════════════════════════════════════════════


class CreateUserScreen(ModalScreen[dict | None]):
    """Modal screen for creating a new user.

    Overlays the main app with username and email input fields.
    Dismisses with a dict of user data on submit, or None on cancel.
    """

    CSS = """
    CreateUserScreen {
        align: center middle;
    }
    #dialog {
        width: 60;
        height: auto;
        padding: 1 2;
        border: thick $accent;
        background: $surface;
    }
    #dialog Label {
        margin-bottom: 1;
    }
    #dialog Input {
        margin-bottom: 1;
    }
    .buttons {
        height: 3;
        align: center middle;
    }
    .buttons Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Create New User", id="title")
            yield Label("Username:")
            yield Input(placeholder="Lastname, Firstname", id="username")
            yield Label("Email:")
            yield Input(placeholder="user@example.com", id="email")
            with Horizontal(classes="buttons"):
                yield Button("Create", variant="primary", id="submit")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button click events.

        Args:
            event: The button press event with ``button.id`` identifying
                which button was clicked.
        """
        if event.button.id == "submit":
            username = self.query_one("#username", Input).value
            email = self.query_one("#email", Input).value
            if username and email:
                self.dismiss({"username": username, "email": email})
            else:
                self.notify("Username and email are required", severity="error")
        else:
            self.dismiss(None)


class EditUserScreen(ModalScreen[dict | None]):
    """Modal screen for editing an existing user.

    Pre-populates input fields with the current user data.
    Dismisses with updated data on save, or None on cancel.
    """

    CSS = CreateUserScreen.CSS.replace("CreateUserScreen", "EditUserScreen")

    def __init__(self, user: dict) -> None:
        """Initialize with existing user data.

        Args:
            user: User dictionary with ``id``, ``username``, and ``email``.
        """
        super().__init__()
        self.user = user

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(f"Edit User #{self.user['id']}", id="title")
            yield Label("Username:")
            yield Input(value=self.user["username"], id="username")
            yield Label("Email:")
            yield Input(value=self.user["email"], id="email")
            with Horizontal(classes="buttons"):
                yield Button("Save", variant="primary", id="submit")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button click events.

        Args:
            event: The button press event.
        """
        if event.button.id == "submit":
            username = self.query_one("#username", Input).value
            email = self.query_one("#email", Input).value
            if username and email:
                self.dismiss({"username": username, "email": email})
            else:
                self.notify("Username and email are required", severity="error")
        else:
            self.dismiss(None)


class CreateTaskScreen(ModalScreen[dict | None]):
    """Modal screen for creating a new task.

    Displays input fields for title, details, assignee, and tags.
    Shows available users for assignee selection.
    """

    CSS = """
    CreateTaskScreen {
        align: center middle;
    }
    #dialog {
        width: 70;
        height: auto;
        padding: 1 2;
        border: thick $accent;
        background: $surface;
    }
    #dialog Label {
        margin-bottom: 1;
    }
    #dialog Input {
        margin-bottom: 1;
    }
    .buttons {
        height: 3;
        align: center middle;
    }
    .buttons Button {
        margin: 0 1;
    }
    """

    def __init__(self, users: list[dict]) -> None:
        """Initialize with list of available users.

        Args:
            users: List of user dicts shown for assignee selection.
        """
        super().__init__()
        self.users = users

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Create New Task", id="title")
            yield Label("Title:")
            yield Input(placeholder="Task title", id="title_input")
            yield Label("Details:")
            yield Input(placeholder="Task details (optional)", id="details")
            yield Label(
                "Assignee ID "
                + str([(u["id"], u["username"]) for u in self.users])
                + ":"
            )
            yield Input(placeholder="User ID", id="assignee_id")
            yield Label("Tag IDs (comma-separated, optional):")
            yield Input(placeholder="1,2,3", id="tag_ids")
            with Horizontal(classes="buttons"):
                yield Button("Create", variant="primary", id="submit")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button click events.

        Args:
            event: The button press event.
        """
        if event.button.id == "submit":
            title = self.query_one("#title_input", Input).value
            details = self.query_one("#details", Input).value
            assignee_id = self.query_one("#assignee_id", Input).value
            tag_ids_str = self.query_one("#tag_ids", Input).value

            if not title or not assignee_id:
                self.notify("Title and assignee ID are required", severity="error")
                return

            tag_ids = []
            if tag_ids_str.strip():
                tag_ids = [
                    int(x.strip())
                    for x in tag_ids_str.split(",")
                    if x.strip().isdigit()
                ]

            self.dismiss(
                {
                    "title": title,
                    "details": details,
                    "assignee_id": int(assignee_id),
                    "tag_ids": tag_ids,
                }
            )
        else:
            self.dismiss(None)


class CreateTagScreen(ModalScreen[dict | None]):
    """Modal screen for creating a new tag.

    Prompts for a tag name. Dismisses with a dict on submit
    or None on cancel.
    """

    CSS = CreateUserScreen.CSS.replace("CreateUserScreen", "CreateTagScreen")

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Create New Tag", id="title")
            yield Label("Name:")
            yield Input(placeholder="Tag name", id="name")
            with Horizontal(classes="buttons"):
                yield Button("Create", variant="primary", id="submit")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button click events.

        Args:
            event: The button press event.
        """
        if event.button.id == "submit":
            name = self.query_one("#name", Input).value
            if name:
                self.dismiss({"name": name})
            else:
                self.notify("Tag name is required", severity="error")
        else:
            self.dismiss(None)


class EditTagScreen(ModalScreen[dict | None]):
    """Modal screen for editing an existing tag.

    Pre-populates the name input with the current tag name.
    """

    CSS = CreateUserScreen.CSS.replace("CreateUserScreen", "EditTagScreen")

    def __init__(self, tag: dict) -> None:
        """Initialize with existing tag data.

        Args:
            tag: Tag dictionary with ``id`` and ``name``.
        """
        super().__init__()
        self.tag = tag

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(f"Edit Tag #{self.tag['id']}", id="title")
            yield Label("Name:")
            yield Input(value=self.tag["name"], id="name")
            with Horizontal(classes="buttons"):
                yield Button("Save", variant="primary", id="submit")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button click events.

        Args:
            event: The button press event.
        """
        if event.button.id == "submit":
            name = self.query_one("#name", Input).value
            if name:
                self.dismiss({"name": name})
            else:
                self.notify("Tag name is required", severity="error")
        else:
            self.dismiss(None)


class ConfirmDeleteScreen(ModalScreen[bool]):
    """Modal screen for confirming a delete operation.

    Displays a confirmation message and Delete/Cancel buttons.
    Dismisses with True if confirmed, False otherwise.
    """

    CSS = """
    ConfirmDeleteScreen {
        align: center middle;
    }
    #dialog {
        width: 50;
        height: auto;
        padding: 1 2;
        border: thick $error;
        background: $surface;
    }
    .buttons {
        height: 3;
        align: center middle;
    }
    .buttons Button {
        margin: 0 1;
    }
    """

    def __init__(self, message: str) -> None:
        """Initialize with a confirmation prompt.

        Args:
            message: Text displayed to the user for confirmation.
        """
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self.message)
            with Horizontal(classes="buttons"):
                yield Button("Delete", variant="error", id="confirm")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button click events.

        Args:
            event: The button press event.
        """
        self.dismiss(event.button.id == "confirm")


# ═══════════════════════════════════════════════════════════════
# Main Application
# ═══════════════════════════════════════════════════════════════


class TaskManagerApp(App):
    """
    Textual TUI application for the Task Manager API

    This app provides a terminal-based interface for managing users,
    tasks, and tags through the REST API.

    Key Bindings:
        c - Create a new item in the active tab
        e - Edit the selected item
        d - Delete the selected item
        t - Toggle task completion (tasks tab only)
        r - Refresh the active tab's data
        q - Quit the application
    """

    TITLE = "Task Manager"

    # Key bindings - these map keyboard keys to action methods
    BINDINGS = [
        Binding("c", "create", "Create", show=True),
        Binding("e", "edit", "Edit", show=True),
        Binding("d", "delete", "Delete", show=True),
        Binding("t", "toggle", "Toggle Done", show=True),
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
            api_url: Base URL of the task_manager_07 API server.
        """
        super().__init__()
        self.api = TaskManagerAPI(api_url)

    def compose(self) -> ComposeResult:
        """Build the UI layout.

        Yields:
            Widget: UI widgets in display order — header, tabbed
                content with DataTables, status bar, and footer.
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
        """Set up DataTable columns and load initial data.

        Called when the app is first mounted (ready to display).
        """
        # Set up Users table columns
        users_table = self.query_one("#users-table", DataTable)
        users_table.add_columns("ID", "Username", "Email", "Tasks")
        users_table.cursor_type = "row"

        # Set up Tasks table columns
        tasks_table = self.query_one("#tasks-table", DataTable)
        tasks_table.add_columns("ID", "Title", "Assignee", "Done", "Tags")
        tasks_table.cursor_type = "row"

        # Set up Tags table columns
        tags_table = self.query_one("#tags-table", DataTable)
        tags_table.add_columns("ID", "Name", "Tasks")
        tags_table.cursor_type = "row"

        # Load all data
        self.load_users()
        self.load_tasks()
        self.load_tags()

    # ── Data Loading ──────────────────────────────────────────────

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

    def load_tasks(self) -> None:
        """Fetch tasks from API and populate the tasks table."""
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
            table.add_row(
                str(task["id"]),
                task["title"],
                task["assignee"],
                "Yes" if task["is_done"] else "No",
                ", ".join(task.get("tags", [])),
                key=str(task["id"]),
            )
        self._set_status(f"Loaded {len(tasks)} tasks")

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

    # ── Helper methods ──────────────────────────────────────────

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

    def _get_selected_id(self, table_id: str) -> int | None:
        """Get the ID from the currently selected row in a DataTable.

        Args:
            table_id: The CSS ID of the DataTable widget.

        Returns:
            int | None: The selected row's ID, or None if no rows.
        """
        table = self.query_one(f"#{table_id}", DataTable)
        if table.row_count == 0:
            return None
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        return int(row_key.value)

    # ── Action Methods (bound to keys) ──────────────────────────

    def action_refresh(self) -> None:
        """Refresh data for the active tab."""
        tab = self._get_active_tab()
        if tab == "users":
            self.load_users()
        elif tab == "tasks":
            self.load_tasks()
        else:
            self.load_tags()

    def action_create(self) -> None:
        """Open create form for the active tab's resource type."""
        tab = self._get_active_tab()
        if tab == "users":
            self.push_screen(CreateUserScreen(), self._on_create_user)
        elif tab == "tasks":
            # Fetch users list for the assignee dropdown, then open form
            try:
                users = self.api.get_users()
            except httpx.HTTPError:
                self._set_status("Error: Could not fetch users")
                return
            self.push_screen(CreateTaskScreen(users), self._on_create_task)
        else:
            self.push_screen(CreateTagScreen(), self._on_create_tag)

    def action_edit(self) -> None:
        """Open edit form for the selected item."""
        tab = self._get_active_tab()
        if tab == "users":
            user_id = self._get_selected_id("users-table")
            if user_id is None:
                return
            try:
                user = self.api.get_user(user_id)
            except httpx.HTTPError:
                self._set_status(f"Error: Could not fetch user {user_id}")
                return
            self.push_screen(EditUserScreen(user), self._on_edit_user_result)
        elif tab == "tasks":
            self.notify("Use toggle (t) to change task status", severity="info")
        else:
            tag_id = self._get_selected_id("tags-table")
            if tag_id is None:
                return
            try:
                tag = self.api.get_tag(tag_id)
            except httpx.HTTPError:
                self._set_status(f"Error: Could not fetch tag {tag_id}")
                return
            self.push_screen(EditTagScreen(tag), self._on_edit_tag_result)

    def action_delete(self) -> None:
        """Confirm and delete the selected item."""
        tab = self._get_active_tab()
        table_id = f"{tab}-table"
        item_id = self._get_selected_id(table_id)
        if item_id is None:
            return
        self.push_screen(
            ConfirmDeleteScreen(f"Delete {tab[:-1]} #{item_id}?"),
            lambda confirmed: self._on_delete_confirmed(confirmed, tab, item_id),
        )

    def action_toggle(self) -> None:
        """Toggle task completion status (tasks tab only)."""
        if self._get_active_tab() != "tasks":
            self.notify("Toggle only works on the Tasks tab", severity="info")
            return
        task_id = self._get_selected_id("tasks-table")
        if task_id is not None:
            self._do_toggle_task(task_id)

    # ── Callbacks for modal screens ─────────────────────────────

    def _on_create_user(self, result: dict | None) -> None:
        """Handle CreateUserScreen dismissal.

        Args:
            result: User data dict if submitted, None if cancelled.
        """
        if result is None:
            return
        try:
            user = self.api.create_user(result["username"], result["email"])
            self._set_status(f"Created user: {user['username']}")
            self.load_users()
        except httpx.HTTPStatusError as e:
            error = e.response.json().get("error", "Unknown error")
            self._set_status(f"Error: {error}")

    def _on_create_task(self, result: dict | None) -> None:
        """Handle CreateTaskScreen dismissal.

        Args:
            result: Task data dict if submitted, None if cancelled.
        """
        if result is None:
            return
        try:
            task = self.api.create_task(
                result["title"],
                result["assignee_id"],
                result.get("details", ""),
                result.get("tag_ids", []),
            )
            self._set_status(f"Created task: {task['title']}")
            self.load_tasks()
        except httpx.HTTPStatusError as e:
            error = e.response.json().get("error", "Unknown error")
            self._set_status(f"Error: {error}")

    def _on_create_tag(self, result: dict | None) -> None:
        """Handle CreateTagScreen dismissal.

        Args:
            result: Tag data dict if submitted, None if cancelled.
        """
        if result is None:
            return
        try:
            tag = self.api.create_tag(result["name"])
            self._set_status(f"Created tag: {tag['name']}")
            self.load_tags()
        except httpx.HTTPStatusError as e:
            error = e.response.json().get("error", "Unknown error")
            self._set_status(f"Error: {error}")

    def _on_edit_user_result(self, result: dict | None) -> None:
        """Handle EditUserScreen dismissal.

        Args:
            result: Updated user data dict if saved, None if cancelled.
        """
        if result is None:
            return
        user_id = self._get_selected_id("users-table")
        if user_id is None:
            return
        try:
            user = self.api.update_user(user_id, result["username"], result["email"])
            self._set_status(f"Updated user: {user['username']}")
            self.load_users()
        except httpx.HTTPStatusError as e:
            error = e.response.json().get("error", "Unknown error")
            self._set_status(f"Error: {error}")

    def _on_edit_tag_result(self, result: dict | None) -> None:
        """Handle EditTagScreen dismissal.

        Args:
            result: Updated tag data dict if saved, None if cancelled.
        """
        if result is None:
            return
        tag_id = self._get_selected_id("tags-table")
        if tag_id is None:
            return
        try:
            tag = self.api.update_tag(tag_id, result["name"])
            self._set_status(f"Updated tag: {tag['name']}")
            self.load_tags()
        except httpx.HTTPStatusError as e:
            error = e.response.json().get("error", "Unknown error")
            self._set_status(f"Error: {error}")

    def _on_delete_confirmed(
        self, confirmed: bool, resource: str, item_id: int
    ) -> None:
        """Handle ConfirmDeleteScreen dismissal.

        Args:
            confirmed: True if the user confirmed deletion.
            resource: Resource type (``"users"``, ``"tasks"``, or ``"tags"``).
            item_id: The ID of the item to delete.
        """
        if not confirmed:
            return
        try:
            if resource == "users":
                result = self.api.delete_user(item_id)
            elif resource == "tasks":
                result = self.api.delete_task(item_id)
            else:
                result = self.api.delete_tag(item_id)

            self._set_status(result.get("message", "Deleted"))
            # Refresh the relevant table
            if resource == "users":
                self.load_users()
            elif resource == "tasks":
                self.load_tasks()
            else:
                self.load_tags()
        except httpx.HTTPStatusError as e:
            error = e.response.json().get("error", "Unknown error")
            self._set_status(f"Error: {error}")

    def _do_toggle_task(self, task_id: int) -> None:
        """Toggle a task's completion status via the API.

        Args:
            task_id: The ID of the task to toggle.
        """
        try:
            task = self.api.toggle_task(task_id)
            status = "completed" if task["is_done"] else "active"
            self._set_status(f"Task '{task['title']}' marked as {status}")
            self.load_tasks()
        except httpx.HTTPStatusError as e:
            error = e.response.json().get("error", "Unknown error")
            self._set_status(f"Error: {error}")
