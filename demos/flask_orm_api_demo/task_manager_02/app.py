"""
task_manager_02 - Task manager JSON API with blueprints
This demonstrates how to organize routes using Flask blueprints
Blueprints help keep code organized by grouping related routes together
"""

# Import the tasks blueprint from the tasks module in this package
# Support both running as a package and as a script
try:
    # importing as part of package
    from . import tasks
except ImportError:
    # importing when running script
    import tasks

from flask import Flask


def create_app():
    """
    Application factory function
    Creates and configures the Flask application with blueprints

    Blueprints allow you to organize your application into modules
    Each blueprint can have its own routes, templates, and static files

    Returns:
        Flask: Configured Flask application with registered blueprints
    """
    # Create the Flask application instance
    app = Flask(__name__)

    # Register the tasks blueprint with the application
    # This makes all routes defined in tasks.py available in our app
    # After registration, Flask knows about the routes in the blueprint
    app.register_blueprint(tasks.blue_print)

    # Return the configured application
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="localhost", port=8080, debug=True)
