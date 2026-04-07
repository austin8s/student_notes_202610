"""TUI System Monitor — a Textual dashboard using the Monitor class.

A three-section dashboard that exercises the Textual concepts presented
in the gui_textual.md resource.  The layout follows the same pattern as
the Fleet Monitor Dashboard:

    ┌─────────────────────────────────────────────────────────────┐
    │ Header                                                      │
    ├──────────────────────────┬──────────────────────────────────┤
    │ Data List (DataTable)    │ Detail Panel (Static / widgets)  │
    │  select a data type →    │  summary for the selection       │
    ├──────────────────────────┴──────────────────────────────────┤
    │ Specifics Table (DataTable) — tabular detail for selection  │
    ├─────────────────────────────────────────────────────────────┤
    │ Footer (key bindings)                                       │
    └─────────────────────────────────────────────────────────────┘

Concepts demonstrated:
    - App subclassing (TITLE, SUB_TITLE, BINDINGS, CSS_PATH, compose, on_mount)
    - Custom widget — subclassing Static (DetailPanel)
    - Custom widget — subclassing Widget (MetricBar with compose/children)
    - Containers (Horizontal, VerticalScroll)
    - compose() with yield and container nesting
    - Events and messages (on_data_table_row_selected)
    - Key bindings and action methods
    - DOM queries (query_one, query)
    - DataTable (columns, rows, keys, clear, get_row, cursor_type,
      zebra_stripes, Rich Text styling)
    - Notifications (self.notify — informational, warning, and error toasts)
    - Reactive attributes with watch and validate methods
    - Timers (set_interval, timer.stop)
    - Dynamic widget mounting and removal
    - Instance attributes for state
    - async/await — used for operations that modify the widget tree

A note on async/await in this application:
    Textual's mount() and remove_children() modify the widget tree.  These
    operations are *asynchronous* — they return an "awaitable" object rather
    than completing immediately.  If you call them without ``await``, Python
    schedules the work but moves to the next line before the work finishes.
    That causes "DuplicateIds" errors because old widgets haven't been
    removed by the time new widgets with the same IDs are added.

    The fix: mark the method with ``async def`` and put ``await`` in front of
    every call that modifies the widget tree.  ``await`` tells Python:
    "pause here until this operation finishes, then continue to the next
    line."  Textual's event loop handles the pause — the UI stays responsive.

    Rule of thumb:
        - If a method calls ``await``, it must be declared ``async def``.
        - If you call an ``async def`` method, you must ``await`` it.
        - Textual natively supports async event handlers, action methods,
          and timer callbacks — no extra setup is needed.
"""

import platform

from monitor import Monitor
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DataTable, Footer, Header, Static

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def format_bytes(n: int) -> str:
    """Formats a byte count as a human-readable string.

    Args:
        n: Number of bytes.

    Returns:
        Formatted string with appropriate unit (e.g., '4.2 GB').
    """
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def _style_percent(value: float) -> Text:
    """Returns a color-coded Rich Text for a usage percentage.

    Args:
        value: Usage percentage (0-100).

    Returns:
        A Rich Text object styled green, yellow, or red.
    """
    label = f"{value:.1f}%"
    if value >= 90:
        return Text(label, style="bold red")
    if value >= 70:
        return Text(label, style="bold yellow")
    return Text(label, style="bold green")


# ---------------------------------------------------------------------------
# Custom widgets
# ---------------------------------------------------------------------------


class DetailPanel(Static):
    """A text panel mounted dynamically in the detail area.

    Subclasses Static — call .update() to change the displayed text.
    Demonstrates the Static-subclass pattern and dynamic mounting/removal
    (Section 11 of the guide).
    """


class MetricBar(Widget):
    """A composite widget that shows a labelled text-based usage bar.

    Subclasses Widget and uses compose() to yield child Static widgets.
    Demonstrates the Widget-subclass pattern with child composition and
    DOM queries on child widgets.

    Args:
        label: The metric name shown above the bar.
        id: Unique widget identifier for DOM queries.
    """

    def __init__(self, label: str, id: str) -> None:
        """Initializes the MetricBar with a label.

        Args:
            label: Display name for this metric (e.g., 'CPU', 'Memory').
            id: Unique widget identifier for DOM queries.
        """
        super().__init__(id=id)
        self.label = label

    def compose(self) -> ComposeResult:
        """Yields three child Static widgets: label, bar, and detail line."""
        yield Static(self.label, id=f"{self.id}-label")
        yield Static("", id=f"{self.id}-bar")
        yield Static("", id=f"{self.id}-detail")

    def update_bar(self, percent: float, detail: str = "") -> None:
        """Updates the usage bar and optional detail text.

        Args:
            percent: Usage percentage (0-100).
            detail: Optional detail string shown below the bar.
        """
        filled = int(percent / 5)  # 20 characters wide
        bar = "█" * filled + "░" * (20 - filled)
        self.query_one(f"#{self.id}-bar", Static).update(f"[{bar}] {percent:.1f}%")
        if detail:
            self.query_one(f"#{self.id}-detail", Static).update(detail)


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

# Keys used in the system-info table to identify each attribute row
_KEY_HOSTNAME = "hostname"
_KEY_OS = "os"
_KEY_OS_VERSION = "os-version"
_KEY_CPU = "cpu"
_KEY_MEMORY = "memory"
_KEY_DISKS = "disks"
_KEY_NETWORK = "network"


class SystemMonitorApp(App):
    """A three-section TUI dashboard for local system monitoring.

    Top-left: system attribute list.  Top-right: detail panel with
    summary text and optional MetricBar widgets.  Bottom: a DataTable
    showing specifics (disk partitions, network interfaces, etc.).

    Attributes:
        refresh_seconds: How often live metrics are refreshed (reactive).
    """

    TITLE = "System Monitor"
    SUB_TITLE = "Select an attribute to view details"
    CSS_PATH = "monitor.tcss"

    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("d", "toggle_dark", "Dark Mode"),
        ("f", "faster", "Faster"),
        ("s", "slower", "Slower"),
        ("q", "quit", "Quit"),
    ]

    # Reactive attribute — changing this value triggers watch and validate
    refresh_seconds: reactive[int] = reactive(3)

    def __init__(self) -> None:
        """Initializes the app with a Monitor and no active timer."""
        super().__init__()
        self.monitor = Monitor()  # Instance attribute — Monitor instance
        self._timer = None  # Instance attribute — active timer
        self._selected_key = None  # Instance attribute — currently selected row
        # Guard against concurrent refreshes — if a refresh is already
        # awaiting remove_children()/mount(), a second timer tick must
        # skip rather than start a parallel rebuild (which would cause
        # DuplicateIds errors).
        self._refreshing = False

    def compose(self) -> ComposeResult:
        """Builds the three-section layout matching the dashboard pattern."""
        yield Header()
        with Horizontal(id="top-pane"):
            yield DataTable(id="sys-table")
            yield VerticalScroll(id="detail-panel")
        yield DataTable(id="specifics-table")
        yield Static(id="refresh-info")
        yield Footer()

    def on_mount(self) -> None:
        """Populates the system-info table and starts the refresh timer."""
        metrics = self.monitor.metrics

        # -- System-info table (top-left) --
        table = self.query_one("#sys-table", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("Attribute", "Value")

        table.add_row("Hostname", platform.node(), key=_KEY_HOSTNAME)
        table.add_row("OS", metrics.os_type, key=_KEY_OS)
        table.add_row("OS Version", metrics.os_version, key=_KEY_OS_VERSION)
        table.add_row("CPU", f"{metrics.cpu_count} cores", key=_KEY_CPU)
        table.add_row("Memory", format_bytes(metrics.memory.total), key=_KEY_MEMORY)
        table.add_row(
            "Disks",
            f"{len(metrics.disks)} partition(s)",
            key=_KEY_DISKS,
        )
        table.add_row(
            "Network",
            f"{len(metrics.network)} interface(s)",
            key=_KEY_NETWORK,
        )

        # -- Detail panel (top-right) — start with a hint --
        self.query_one("#detail-panel").mount(
            Static("← Select an attribute to view details", id="detail-content")
        )

        # -- Specifics table (bottom) — starts empty --
        spec_table = self.query_one("#specifics-table", DataTable)
        spec_table.cursor_type = "row"
        spec_table.zebra_stripes = True

        # Start the auto-refresh timer for live metrics
        self._timer = self.set_interval(self.refresh_seconds, self._refresh_detail)

    # ---- detail rendering ----------------------------------------------------
    #
    # Why async/await?
    # Textual's remove_children() and mount() modify the widget tree
    # asynchronously.  Using "await" ensures the old widgets are fully
    # removed before new widgets with the same IDs are added.  Without
    # await, both old and new widgets would exist simultaneously,
    # causing DuplicateIds errors.
    #
    # Every method in this chain is "async def" because it ultimately
    # calls await on a Textual operation.  The rule is simple:
    #   - If a method uses "await", it must be "async def".
    #   - If you call an "async def" method, you must "await" it.
    # -----------------------------------------------------------------------

    async def _clear_detail(self) -> None:
        """Removes all dynamically mounted widgets from the detail panel."""
        # await = wait for all children to be fully removed before returning.
        # Without await, the removal would be scheduled but not yet complete.
        await self.query_one("#detail-panel", VerticalScroll).remove_children()

    def _clear_specifics(self) -> None:
        """Clears the bottom specifics table (columns and rows)."""
        self.query_one("#specifics-table", DataTable).clear(columns=True)

    async def _show_detail_text(self, text: str) -> None:
        """Mounts a DetailPanel with the given text in the detail area.

        Args:
            text: The content to display.
        """
        # await _clear_detail() — pauses until old widgets are gone
        await self._clear_detail()
        panel = DetailPanel(text, id="detail-content")
        # await mount() — pauses until the new widget is in the DOM
        await self.query_one("#detail-panel", VerticalScroll).mount(panel)

    async def _show_hostname(self) -> None:
        """Displays hostname details in the detail panel."""
        hostname = platform.node()
        await self._show_detail_text(f"  [bold underline]Hostname[/]\n\n  {hostname}\n")
        self._clear_specifics()

    async def _show_os(self) -> None:
        """Displays OS type details in the detail panel."""
        await self._show_detail_text(
            f"  [bold underline]Operating System[/]\n\n"
            f"  Type:  {self.monitor.os_type}\n"
        )
        self._clear_specifics()

    async def _show_os_version(self) -> None:
        """Displays OS version details in the detail panel."""
        await self._show_detail_text(
            f"  [bold underline]OS Version[/]\n\n"
            f"  {self.monitor.os_type} {self.monitor.os_version}\n"
        )
        self._clear_specifics()

    async def _show_cpu(self) -> None:
        """Displays CPU details with a live usage bar in the detail panel."""
        await self._clear_detail()  # await = old widgets fully removed
        area = self.query_one("#detail-panel", VerticalScroll)
        await area.mount(  # await = DetailPanel fully added before MetricBar
            DetailPanel(
                f"  [bold underline]CPU[/]\n\n"
                f"  Physical cores: {self.monitor.cpu_count}\n",
                id="cpu-info",
            )
        )
        bar = MetricBar("  CPU Usage", id="cpu-bar")
        await area.mount(bar)  # await = bar is in the DOM; safe to query children
        # Now that the bar is mounted, we can update its child widgets
        bar.update_bar(self.monitor.cpu_percent)

        # Bottom table — single row with current CPU snapshot
        self._clear_specifics()
        spec = self.query_one("#specifics-table", DataTable)
        spec.add_columns("Metric", "Value")
        spec.add_row("Cores", str(self.monitor.cpu_count))
        spec.add_row("Usage", _style_percent(self.monitor.cpu_percent))

    async def _show_memory(self) -> None:
        """Displays memory details with a live usage bar in the detail panel."""
        await self._clear_detail()  # await = old widgets fully removed
        mem = self.monitor.memory
        area = self.query_one("#detail-panel", VerticalScroll)
        await area.mount(  # await = DetailPanel added before MetricBar
            DetailPanel(
                f"  [bold underline]Memory[/]\n\n"
                f"  Total:  {format_bytes(mem.total)}\n"
                f"  Used:   {format_bytes(mem.used)}\n"
                f"  Free:   {format_bytes(mem.total - mem.used)}\n",
                id="mem-info",
            )
        )
        bar = MetricBar("  Memory Usage", id="mem-bar")
        await area.mount(bar)  # await = bar is in the DOM; safe to query children
        bar.update_bar(
            mem.percent,
            detail=f"  {format_bytes(mem.used)} / {format_bytes(mem.total)}",
        )

        # Bottom table — memory breakdown
        self._clear_specifics()
        spec = self.query_one("#specifics-table", DataTable)
        spec.add_columns("Metric", "Value")
        spec.add_row("Total", format_bytes(mem.total))
        spec.add_row("Used", format_bytes(mem.used))
        spec.add_row("Free", format_bytes(mem.total - mem.used))
        spec.add_row("Usage", _style_percent(mem.percent))

    async def _show_disks(self) -> None:
        """Displays disk summary in detail panel, partitions in specifics."""
        disks = self.monitor.disks
        await self._show_detail_text(
            f"  [bold underline]Disk Partitions[/]\n\n"
            f"  {len(disks)} partition(s) detected\n"
        )

        # Bottom table — one row per partition
        self._clear_specifics()
        spec = self.query_one("#specifics-table", DataTable)
        spec.add_columns("Device", "Mount", "Type", "Total", "Used", "Free", "Use%")
        for disk in disks:
            spec.add_row(
                disk.device,
                disk.mountpoint,
                disk.fstype,
                format_bytes(disk.total),
                format_bytes(disk.used),
                format_bytes(disk.free),
                _style_percent(disk.percent),
                key=disk.mountpoint,
            )

    async def _show_network(self) -> None:
        """Displays network summary in detail panel, interfaces in specifics."""
        devs = self.monitor.network
        await self._show_detail_text(
            f"  [bold underline]Network Interfaces[/]\n\n"
            f"  {len(devs)} interface(s) detected\n"
        )

        # Bottom table — one row per interface
        self._clear_specifics()
        spec = self.query_one("#specifics-table", DataTable)
        spec.add_columns("Interface", "IPs", "Sent (Δ)", "Recv (Δ)")
        for dev in devs:
            spec.add_row(
                dev.name,
                ", ".join(dev.ips) if dev.ips else "—",
                format_bytes(dev.bytes_sent_since_last),
                format_bytes(dev.bytes_recv_since_last),
                key=dev.name,
            )

    # Map row keys to their detail-rendering methods
    _DETAIL_VIEWS = {
        _KEY_HOSTNAME: _show_hostname,
        _KEY_OS: _show_os,
        _KEY_OS_VERSION: _show_os_version,
        _KEY_CPU: _show_cpu,
        _KEY_MEMORY: _show_memory,
        _KEY_DISKS: _show_disks,
        _KEY_NETWORK: _show_network,
    }

    async def _show_selected_detail(self) -> None:
        """Renders the detail view for the currently selected attribute."""
        if self._selected_key is None:
            return
        # Reentrance guard — if a previous refresh is still running
        # (e.g., awaiting remove_children), skip this call to avoid
        # mounting duplicate widgets.  The next timer tick will retry.
        if self._refreshing:
            return
        self._refreshing = True
        try:
            view_method = self._DETAIL_VIEWS.get(self._selected_key)
            if view_method:
                # The view methods are all async — we must await them
                await view_method(self)
        finally:
            # Always release the guard, even if an exception occurs
            self._refreshing = False

    async def _refresh_detail(self) -> None:
        """Timer callback — refreshes the detail panel for live metrics.

        Only CPU and memory panels contain data that changes over time.
        Network traffic deltas also refresh when that view is active.

        Textual's set_interval() natively supports async callbacks —
        no extra setup needed.
        """
        if self._selected_key in (_KEY_CPU, _KEY_MEMORY, _KEY_NETWORK):
            await self._show_selected_detail()

        # Update the refresh-info line
        self.query_one("#refresh-info", Static).update(
            f"  Refresh: every {self.refresh_seconds}s  │  f = faster  s = slower"
        )

    # ---- event handlers ------------------------------------------------------

    async def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Displays the detail view for the selected system attribute.

        Handles row selection from the system-info table (top-left).
        Uses ``get_row()`` to read back the cell values from the
        selected row — the same technique used in the Fleet Monitor
        Dashboard to extract a server ID from a host-table row.

        Textual event handlers can be declared ``async def`` — the
        framework will await them automatically.

        Args:
            event: The row-selected event from a DataTable.
        """
        if event.data_table.id == "sys-table":
            # get_row() returns cell values in column order: [Attribute, Value]
            row = event.data_table.get_row(event.row_key)
            self.sub_title = f"{row[0]}: {row[1]}"
            self._selected_key = str(event.row_key.value)
            self.notify(f"Selected: {row[0]}")
            await self._show_selected_detail()

    async def on_data_table_row_highlighted(
        self, event: DataTable.RowHighlighted
    ) -> None:
        """Updates the detail panel as the cursor moves over data rows."""
        if event.control.id != "sys-table":
            return
        if event.row_key is None:
            return
        self._selected_key = str(event.row_key.value)
        await self._show_selected_detail()

    # ---- reactive: validate + watch ------------------------------------------

    def validate_refresh_seconds(self, value: int) -> int:
        """Constrains the refresh interval between 1 and 30 seconds.

        Args:
            value: The proposed new interval.

        Returns:
            The clamped interval value.
        """
        clamped = max(1, min(30, value))
        if clamped != value:
            self.notify(
                f"Refresh clamped to {clamped}s (range: 1–30)",
                severity="warning",
            )
        return clamped

    def watch_refresh_seconds(self, old_value: int, new_value: int) -> None:
        """Restarts the auto-refresh timer when the interval changes.

        Args:
            old_value: The previous refresh interval.
            new_value: The new refresh interval.
        """
        if self._timer is not None:
            self._timer.stop()
        self._timer = self.set_interval(new_value, self._refresh_detail)
        self.query_one("#refresh-info", Static).update(
            f"  Refresh: every {new_value}s  │  f = faster  s = slower"
        )

    # ---- action methods ------------------------------------------------------

    async def action_refresh(self) -> None:
        """Manually refreshes the current detail view.

        Textual action methods can be ``async def`` — the framework
        will await them when the key binding is triggered.
        """
        await self._show_selected_detail()

    def action_faster(self) -> None:
        """Decreases the refresh interval by 1 second."""
        self.refresh_seconds -= 1
        self.notify(f"Refresh: every {self.refresh_seconds}s")

    def action_slower(self) -> None:
        """Increases the refresh interval by 1 second."""
        self.refresh_seconds += 1
        self.notify(f"Refresh: every {self.refresh_seconds}s")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = SystemMonitorApp()
    app.run()
