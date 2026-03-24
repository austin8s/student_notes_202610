"""
task_manager_01 - Task manager JSON API with factory pattern
This demonstrates the application factory pattern (recommended approach)
Returning a dict from a view function automatically produces a JSON response.
"""

# from task_manager_01 import create_app
from flask import Flask


def create_app():
    """
    Application factory function
    This function creates and configures a Flask application instance

    Why use a factory function?
    - Easier to test (you can create multiple app instances)
    - Cleaner code organization
    - Can create apps with different configurations

    Returns:
        Flask: A configured Flask application ready to handle requests
    """
    # Create the Flask application instance
    # __name__ is a special Python variable that contains the name of this module
    # Flask uses it to locate resources like templates and static files
    app = Flask(__name__)

    # Register a route using the @app.route decorator
    # This tells Flask: "when someone visits '/', call the home() function"
    @app.route("/")
    def home():
        """
        View function for the home page
        This function is called whenever someone visits the root URL (/)

        Returns:
            dict: JSON response automatically serialized by Flask
        """
        return {"message": "Task Manager 01 - Hello World!"}

    # Return the configured application
    # The run script will use this to start the development server
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
