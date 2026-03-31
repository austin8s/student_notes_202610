"""
Entry script for the fleet monitoring aggregation server.
"""

from fleet_api import create_app

app = create_app()

if __name__ == "__main__":
    # Note: The `port` argument is specified in the `uv run` command
    # in the instructions, e.g., `uv run flask --app run_server run --debug --port 5001`
    app.run()
