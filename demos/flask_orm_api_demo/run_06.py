"""
Entry script for task_manager_06

Usage:
    uv run python run_06.py
"""

from task_manager_06 import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
