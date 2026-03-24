"""
Entry script for task_manager_05

Usage:
    uv run python run_05.py
"""

from task_manager_05 import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
