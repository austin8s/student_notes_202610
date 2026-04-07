"""Inventory Dashboard Demo.

A simple Textual TUI application that demonstrates the major concepts
covered in the gui_textual introduction: App, widgets, key bindings,
DataTable, events, and timers.

Run::

    python app.py
"""

from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header, Static


class InventoryApp(App):
    """A simple inventory dashboard.

    Demonstrates:
        - ``App`` subclass with ``BINDINGS`` and ``compose()``
        - ``DataTable`` with columns, rows, row cursor, and zebra stripes
        - Rich ``Text`` objects for color-coded status values
        - Event handling with ``on_data_table_row_selected``
        - Actions for key bindings: refresh, add, delete
        - DOM queries with ``query_one()``
    """

    BINDINGS = [
        ("a", "add_item", "Add Item"),
        ("d", "delete_item", "Delete"),
        ("r", "refresh", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Build the application layout.

        Yields:
            The widgets that make up the dashboard interface.
        """
        yield Header()
        yield DataTable(id="inventory")
        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Configure the table and load initial data after the app is ready."""
        table = self.query_one("#inventory", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("Item", "Qty", "Status")
        self._load_data(table)

    def _load_data(self, table: DataTable) -> None:
        """Populate the table with sample inventory items.

        Args:
            table: The DataTable widget to populate.
        """
        items = [
            ("Widget-A", 150, "In Stock"),
            ("Widget-B", 3, "Low Stock"),
            ("Gadget-X", 0, "Out of Stock"),
        ]
        for name, qty, status in items:
            styled_status = self._style_status(status)
            table.add_row(name, str(qty), styled_status, key=name)

    def _style_status(self, status: str) -> Text:
        """Return a color-coded Rich Text object for an inventory status.

        Args:
            status: The status string (e.g. "In Stock", "Low Stock").

        Returns:
            A Rich Text object with appropriate color styling.
        """
        styles = {
            "In Stock": "green",
            "Low Stock": "yellow",
            "Out of Stock": "bold red",
        }
        return Text(status, style=styles.get(status, "white"))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Update the status bar when a row is selected.

        Args:
            event: The row-selected event from the DataTable.
        """
        row = self.query_one("#inventory", DataTable).get_row(event.row_key)
        self.query_one("#status-bar", Static).update(f"Selected: {row[0]}")

    def action_refresh(self) -> None:
        """Clear and reload the inventory table."""
        table = self.query_one("#inventory", DataTable)
        table.clear()
        self._load_data(table)
        self.notify("Inventory refreshed")

    def action_add_item(self) -> None:
        """Placeholder action for adding an item."""
        self.notify("Add item (not implemented in this demo)")

    def action_delete_item(self) -> None:
        """Delete the currently highlighted row from the table."""
        table = self.query_one("#inventory", DataTable)
        if table.row_count > 0:
            row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
            table.remove_row(row_key)
            self.notify("Item deleted")


if __name__ == "__main__":
    app = InventoryApp()
    app.run()
