"""
task_manager_04 - Task manager JSON API with external data from CSV
This demonstrates how to load data from a CSV file and serve it via a JSON API

Key concepts:
- Loading external data (CSV file)
- Storing data in app.config for access throughout the application
- Serving data as JSON responses from API endpoints
- Data type conversion (strings to booleans, lists)
"""

import csv  # Python's built-in CSV library for reading CSV files

from flask import Flask

from . import tasks


def create_app():
    """
    Application factory function
    Creates and configures the Flask application
    Loads task data from CSV file and stores it in app configuration

    This version demonstrates:
    - Loading data from a CSV file
    - Converting CSV rows to dictionaries
    - Storing data in app.config (a dictionary-like object)
    - Making data available to all routes through current_app.config
    - Serving data as JSON API responses

    Returns:
        Flask: Configured Flask application with data and blueprints
    """
    # Create the Flask application instance
    app = Flask(__name__)

    # Register the tasks blueprint
    # This adds all routes from the tasks module to our application
    app.register_blueprint(tasks.blue_print)

    # Define the path to the CSV file containing tasks
    # This file should be in the task_manager_04 directory
    tasks_path = "task_manager_04/tasks.csv"

    # Open and read the CSV file
    # 'with' ensures the file is properly closed after reading
    with open(tasks_path, "r", encoding="utf-8") as tasks_file:
        # csv.DictReader reads CSV and converts each row to a dictionary
        # The first row (header) becomes the keys for each dictionary
        csv_reader = csv.DictReader(tasks_file)

        # Convert CSV rows to list of dictionaries and process data types
        tasks_data = []
        for row in csv_reader:
            # Convert string values to appropriate types
            task = {
                "id": int(row["id"]),
                "title": row["title"],
                "details": row["details"],
                "is_done": row["is_done"].lower()
                == "true",  # Convert string to boolean
                "assignee": row["assignee"],
                "tags": row["tags"].split("|"),  # Split pipe-separated tags into list
            }
            tasks_data.append(task)

    # Store the tasks in the application's configuration dictionary
    # app.config is a special dictionary that's accessible from any view
    # using current_app.config["tasks"]
    # This makes the data available throughout your application
    app.config["tasks"] = tasks_data

    # Return the configured application with loaded data
    return app
