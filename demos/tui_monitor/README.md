# TUI System Monitor

A terminal-based system monitoring dashboard built with
[Textual](https://textual.textualize.io/).  It reads live CPU, memory, disk,
and network metrics through the `Monitor` class and displays them in an
interactive three-section layout.

## Running the Application

```bash
cd subjects/gui_textualize/demo/tui_monitor
uv sync
uv run app.py
```

## Key Bindings

| Key | Action              |
| --- | ------------------- |
| `r` | Refresh metrics     |
| `f` | Faster auto-refresh |
| `s` | Slower auto-refresh |
| `d` | Toggle dark mode    |
| `q` | Quit                |

Select a row in the top-left table to view details in the right panel and
specifics in the bottom table.

## Project Structure

```
tui_monitor/
├── app.py              # Textual application (SystemMonitorApp)
├── monitor.tcss        # Textual CSS stylesheet
├── pyproject.toml      # uv project — dependencies: textual, psutil
└── monitor/            # System metrics package
    ├── __init__.py
    ├── base.py         # Monitor class (CPU, memory, disk, network)
    └── metric_models.py  # Frozen dataclasses for metric data
```

## Concepts

This demo accompanies the
Building Terminal User Interfaces with Textual:gui_textual.md
guide.  See that document for a full explanation of every Textual concept used
here, including `async`/`await` for widget-tree operations and reentrance
guards.
