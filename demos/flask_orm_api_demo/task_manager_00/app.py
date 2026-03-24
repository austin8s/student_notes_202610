"""
task_manager_00 - Simple task manager JSON API without factory pattern
This demonstrates creating a Flask app directly (simplest approach)
Run this file to start the development server

To run this app:
1. Make sure Flask is installed
2. Run: python task_manager_00/app.py
3. Test with: curl http://localhost:8080/
"""

from flask import Flask

# Create a Flask application instance
# Flask() creates the web application object
# __name__ is a special Python variable containing the name of the current module
# Flask uses this to locate resources like templates and static files
app = Flask(__name__)


# Define a route using the @app.route decorator
# A route connects a URL path to a Python function
# When someone visits http://localhost:8080/, Flask calls the home() function
@app.route("/")
def home():
    """
    View function for the home page

    This function runs whenever someone visits the root URL (/)
    Returning a Python dictionary automatically converts the response to JSON format.
    Flask sets the Content-Type header to application/json.

    Returns:
        dict: JSON response with a message field
    """
    return {"message": "Task Manager 00 Hello World!"}


# This conditional checks if we're running this file directly
# (not importing it as a module) as would be done by `flask run`
if __name__ == "__main__":
    # Start the Flask development server
    # Arguments:
    #   host="localhost" - Only accessible from this computer (not from network)
    #   port=8080 - The server will listen on port 8080
    #   debug=True - Enables:
    #     * Auto-reload when code changes
    #     * Detailed error messages in browser
    #     * Interactive debugger for errors
    # WARNING: Never use debug=True in production!
    app.run(host="localhost", port=8080, debug=True)
