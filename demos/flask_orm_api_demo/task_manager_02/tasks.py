"""
Tasks blueprint for task_manager_02
This file contains route definitions organized into a blueprint

A blueprint is like a mini-application that can be registered with the main app
It helps organize related routes, making the code easier to maintain

All view functions return dictionaries which Flask automatically serializes to JSON.
"""

from flask import Blueprint

# Create a blueprint named "tasks"
# Arguments:
#   "tasks" - The name of the blueprint (used in url_for function)
#   __name__ - Tells Flask where this blueprint is defined
#
# Think of a blueprint as a collection of routes that you can plug into your app
blue_print = Blueprint("tasks", __name__)


# Register a route with the blueprint (not the main app)
# The @blue_print.route decorator works just like @app.route
# but the route belongs to this blueprint
@blue_print.route("/")
def home():
    """
    View function for the home page

    This function is called when someone visits the root URL (/)
    Since it's in a blueprint, Flask will only call it after the blueprint
    is registered with the main application

    Returns:
        dict: JSON response with a message field
    """
    return {"message": "Task Manager 02 - Home!"}


# Another route in the same blueprint
@blue_print.route("/about")
def about():
    """
    View function for the about page

    This function is called when someone visits /about

    Returns:
        dict: JSON response with application information
    """
    return {
        "message": "Task Manager 02 - About",
        "description": "A simple todo application",
    }
