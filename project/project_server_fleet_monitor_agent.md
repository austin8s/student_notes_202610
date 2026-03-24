# Part 1 — Agent API Specification

## Overview

In this part you build a Flask REST API that exposes real system metrics as
JSON. The API wraps a provided `monitor` package — you do not need to write any
system-metrics code yourself.

This project directly applies the skills you developed in the **Intro to Flask**
and **Bruno REST API** exercises. You will use the **application factory pattern**
and **blueprints** (from the Flask overview) to structure your code, and return
plain data structures that Flask will automatically serialize to JSON (as covered
in the HTTP and REST review).

Your GitHub Classroom repository already contains everything except the
`agent_api/` package. Your job is to create that package so that the provided
tests pass and the endpoints return the expected JSON.

### What is provided

| File / Folder                              | Purpose |
| ------------------------------------------ | ------- |
| `monitor/`                                 | System metrics collection — `Monitor` class and frozen dataclasses. **Do not modify.** |
| `tests/conftest.py`                        | Shared `monkeypatch` fixture (`mock_psutil`) that stubs all `psutil` and `platform` calls with deterministic fakes. **Do not modify.** |
| `tests/test_monitor.py`                    | Tests for the `monitor` package. Run these first to confirm your environment works. **Do not modify.** |
| `tests/test_agent_api.py`                  | Tests for every `/api/*` endpoint. Your implementation must pass these. **Do not modify.** |
| `run_agent.py`                             | Entry script — imports `create_app()` and starts the Flask development server. **Do not modify.** |
| `pyproject.toml`                           | Project dependencies (Flask, psutil, pytest, etc.). |

### What you build

You create the `agent_api/` package — three files in two directories:

```
agent_api/
├── __init__.py          # Application factory
└── api/
    ├── __init__.py      # Blueprint definition
    └── routes.py        # Route handlers
```

---

## Repository layout

After you create `agent_api/`, the full project tree looks like this:

```
server_fleet_monitor/
├── run_agent.py                 # PROVIDED — entry script
├── pyproject.toml               # PROVIDED — dependencies
├── monitor/                     # PROVIDED — do not modify
│   ├── __init__.py
│   ├── base.py                  # Monitor class
│   └── metric_models.py         # Frozen dataclasses
├── agent_api/                   # YOU CREATE THIS
│   ├── __init__.py              # Application factory
│   └── api/
│       ├── __init__.py          # Blueprint definition
│       └── routes.py            # Route handlers
└── tests/                       # PROVIDED — do not modify
    ├── __init__.py
    ├── conftest.py              # Shared monkeypatch fixtures
    ├── test_monitor.py          # Monitor package tests
    └── test_agent_api.py        # Agent API tests
```

---

## Understanding the provided code

Before writing any code, take time to read and understand what you've been
given. The provided code does the heavy lifting — your Flask API is a thin
wrapper around it.

### `monitor/` package

The `monitor` package collects system metrics using `psutil` and `platform`. It
has **no Flask dependency** — it is plain Python.

**`Monitor` class** (`monitor/base.py`) — the single class you will interact
with. All its metrics are exposed as `@property` attributes:

| Property      | Returns                      | Description |
| ------------- | ---------------------------- | ----------- |
| `os_type`     | `str`                        | Operating system name (e.g. `"Windows"`) |
| `os_version`  | `str`                        | OS release version |
| `cpu_count`   | `int`                        | Number of physical CPUs |
| `cpu_percent` | `float`                      | System-wide CPU usage % |
| `memory`      | `MemoryMetrics`              | Memory usage statistics |
| `disks`       | `list[DiskMetrics]`          | Usage for each disk partition |
| `network`     | `list[NetworkDeviceMetrics]` | Network devices with traffic deltas |
| `metrics`     | `MonitorMetrics`             | Complete snapshot of all the above |

**Metric dataclasses** (`monitor/metric_models.py`) — four frozen dataclasses.
Each has a `to_dict()` method that converts it to a plain dictionary (suitable
for returning as JSON from Flask). `MonitorMetrics` also has `to_json()`.

Read through these files. Pay attention to what `to_dict()` returns for each
dataclass — the tests assert against those exact structures.

### `tests/conftest.py`

This file defines a `mock_psutil` fixture that replaces every `psutil` and
`platform` call with a fake that returns fixed values. Because it lives in
`conftest.py`, pytest makes it automatically available to every test file — no
import needed.

The fake values (e.g. CPU count = 4, CPU percent = 12.5, one disk `sda1` at
`/`) are what the tests assert against. Your API routes don't need to know about
these fakes — they just call the `Monitor` and return whatever it gives them.

### `tests/test_agent_api.py`

This file contains 12 tests that exercise your API. It defines a `client`
fixture that:

1. Depends on `mock_psutil` (so all system calls are stubbed)
2. Calls `create_app()` to build the Flask application
3. Creates a Flask test client

Read through the tests carefully. They tell you:

- What RESTful endpoints (URLs) must exist
- What HTTP methods they respond to (e.g., `GET`)
- What JSON structure each endpoint must return
- What keys and values are expected inside the JSON objects

**The tests are your specification.** If you're unsure what a route should
return, the test for that route is the definitive answer.

---

## Key design requirement: application-wide `Monitor`

The `Monitor` class tracks deltas for CPU and network usage between calls. If
you create a new `Monitor` on every request, those deltas reset each time and
you lose meaningful data.

The correct approach is to create the `Monitor` **once** when the application
starts and share that single instance across all requests. Flask provides a
standard mechanism for this:

1. In your application factory, instantiate the `Monitor` and store it in
   `app.config`
2. In your route handlers, access it via `current_app.config`

This is the scaffolding for your application factory:

```python
from flask import Flask

from monitor import Monitor


def create_app():
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)

    # Create the Monitor ONCE and store it in app.config so every
    # request handler can access the same instance.
    app.config["monitor"] = Monitor()

    # TODO: Register the API Blueprint here

    return app
```

In your route handlers you then access the monitor like this:

```python
from flask import current_app

# Inside a route handler:
monitor = current_app.config["monitor"]
```

`current_app` is a Flask proxy that points to the application handling the
current request. This is how you reach `app.config` from inside a Blueprint
without needing a direct reference to the `app` object.

> **Why not a global variable?** A global `monitor = Monitor()` would execute
> at import time — before the test fixtures have a chance to stub out `psutil`.
> Storing it in `app.config` inside the factory means the `Monitor` is created
> only when `create_app()` is called, which happens *after* the test stubs are
> in place.

---

## What you need to create

You need to create three files. The tests tell you exactly what functions,
classes, and import paths are expected. Read `test_agent_api.py` and
`run_agent.py` to determine:

- What `agent_api/__init__.py` must export
- What the Blueprint should be named and what URL prefix it uses
- What route paths and HTTP methods are required
- What JSON each route handler must return

### File 1: `agent_api/__init__.py`

This is the application factory. Look at `run_agent.py` and
`test_agent_api.py` to see how it is imported and called.

#### Why in `__init__.py`?

As you saw in the modular Flask exercise, a directory becomes a **package** when it
contains an `__init__.py` file. Whatever you define in `__init__.py` becomes
the package's public interface — it's what other code gets when it writes
`from agent_api import ...`. Because the application factory is the *only*
thing external code needs from this package, placing it in `__init__.py` means
both `run_agent.py` and the tests can import it with a clean, short path (just
like `from app import create_app` in your intro exercise):

```python
from agent_api import create_app
```

If `create_app()` lived in a separate module (e.g. `agent_api/factory.py`), the
import would be longer and the package would expose unnecessary internal
structure. The convention of putting the factory in `__init__.py` keeps the
public API of the package minimal and clean.

Responsibilities:

- Create the Flask application
- Store an application-wide `Monitor` instance in `app.config` (see scaffolding
  above)
- Register the API Blueprint

### File 2: `agent_api/api/__init__.py`

This defines the Blueprint. The tests expect all routes to be accessible under
a specific URL prefix (acting as a base path for these REST resources). Read 
the test URLs to determine what that prefix is.

#### Why another `__init__.py`?

The `api/` directory is a sub-package inside
`agent_api`. Its `__init__.py` serves the same role: it defines the package's
public interface. The Blueprint object is the one thing the outer package needs
from `agent_api/api/`, so the application factory can import it cleanly:

```python
from .api import api_bp
```

This pattern — Blueprint defined in the sub-package's `__init__.py`, routes in
a sibling module — is the standard Flask "Blueprint as a package" layout. It
keeps route registration separate from the Blueprint definition while giving the
parent package a single, obvious import target.

One important detail: the `routes` module must be imported **after** the
Blueprint object is defined. This avoids a circular import, since `routes.py`
will import the Blueprint to register its decorators.

### File 3: `agent_api/api/routes.py`

This is where all the route handlers live (your business logic). Each handler
will respond to HTTP GET requests (like you sent via Bruno), access the shared
`Monitor` via `current_app.config`, and return a Python dictionary that Flask
automatically transforms into JSON.

Read the tests to determine:

- How many route handlers you need
- What URL path each one responds to
- What JSON structure each one must return
- Whether to return a dataclass's `to_dict()` output directly, or wrap it in a
  dictionary with a specific key

### A Note on Relative Imports

When you are building a multi-file Python package like `agent_api`, you need to link its internal modules together. You might be tempted to use absolute imports (e.g., `from agent_api.api import api_bp`), but to properly structure this package, you should use **relative imports**.

A relative import uses a dot (`.`) to mean "start looking in the current directory". For example:

- In `agent_api/__init__.py`, to import the blueprint from the `api/` sub-package:
  `from .api import api_bp`
- In `agent_api/api/__init__.py`, to import the routes file from the same directory:
  `from . import routes`
- In `agent_api/api/routes.py`, to import the blueprint defined in its parent `__init__.py`:
  `from . import api_bp`

**Why are they necessary?**  
Using relative imports wires your package together internally without hardcoding the outermost package name (`agent_api`). This is required because different external tools (like `pytest` running tests vs. `flask run` starting the server) load your code from different starting locations. Relative imports ensure that no matter how the package is launched, the internal files can always find each other securely without throwing `ModuleNotFoundError`s. It makes your package truly self-contained and portable!

---

## How to run the project

### Install dependencies

```powershell
uv sync
```

### Verify the provided code

Run the monitor tests first to confirm your environment is set up correctly:

```powershell
uv run pytest tests/test_monitor.py -v
```

These should all pass before you write any code. If they don't, check your
Python version and dependencies.

### Run your tests

As you implement your routes, run the agent API tests:

```powershell
uv run pytest tests/test_agent_api.py -v
```

Run all tests together:

```powershell
uv run pytest -v
```

### Start the development server

Once your implementation passes the tests, start the Flask development server 
(Werkzeug) to try the endpoints manually:

```powershell
uv run flask --app run_agent run --debug
```

The server runs at `http://127.0.0.1:5000`. As you read in the WSGI overview, 
this server listens for connections, parses the HTTP, and matches the URLs 
against your Blueprint routes. Try these in your browser or Bruno:

- `http://127.0.0.1:5000/api/status`
- `http://127.0.0.1:5000/api/cpu_count`
- `http://127.0.0.1:5000/api/metrics`

### Debugging with VS Code

The repository includes a `.vscode/launch.json` with three debug configurations
you can use from the **Run and Debug** panel (`Ctrl+Shift+D`):

| Configuration | What it does |
| --- | --- |
| **Python Debugger: Current File** | Runs whichever file is open in the editor. Useful for quick one-off scripts. |
| **Agent API** | Launches the Flask server via `run_agent.py` under the debugger. Set breakpoints in your route handlers and step through requests. |
| **Monitor** | Runs the `monitor` module directly. Useful for exploring what the provided `Monitor` class returns without starting Flask. |

**To debug your route handlers:**

1. Open the **Run and Debug** panel (`Ctrl+Shift+D`)
2. Select **Agent API** from the dropdown
3. Set a breakpoint in one of your route functions in `routes.py` (click the
   gutter to the left of the line number)
4. Press `F5` to start — the Flask server launches with the debugger attached
5. Send a request (browser, Bruno, or curl) — execution pauses at your
   breakpoint
6. Use the debug toolbar to step through code, inspect variables, and examine
   the `Monitor` output

**To debug tests:**

VS Code can also run individual tests under the debugger. Open the Testing
panel (flask icon in the sidebar), find a failing test, right-click it, and
choose **Debug Test**. This lets you step through both your code and the test
assertions.

---

## Suggested approach

1. **Read the provided code** — understand `Monitor`, the dataclasses, and
   their `to_dict()` output
2. **Read the tests** — `test_agent_api.py` is your specification
3. **Create the package structure** — make the `agent_api/` and `agent_api/api/`
   directories with their `__init__.py` files
4. **Start with the factory** — get `create_app()` working so the `client`
   fixture can build the app
5. **Add the Blueprint** — define it with the correct prefix
6. **Implement one route at a time** — start with `/api/status` (simplest),
   then work through the others
7. **Run the tests after each route** — use `pytest -v` to see which tests
   pass and which remain

---

## Grading

Your implementation will be assessed on whether the provided tests pass. The
detailed rubric is in the
[project overview](project_server_fleet_monitor_overview.md).

| Criterion | Marks |
| --- | --- |
| Application factory creates Flask app and registers Blueprint | 5 |
| `Monitor` stored in `app.config` as an application-wide instance | 3 |
| Blueprint defined with correct URL prefix | 5 |
| All route handlers return correct JSON | 27 |
| All provided tests pass | 8 |
| **Total** | **48** |
