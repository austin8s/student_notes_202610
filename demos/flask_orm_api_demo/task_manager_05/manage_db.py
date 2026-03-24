"""
Database setup script for task_manager_05
Creates database and populates with initial data from CSV

This script demonstrates:
- Creating database tables from Peewee models
- Reading data from CSV files
- Converting CSV data to database records
- Using Peewee to insert data

Run this before starting the application:
    python task_manager_05/manage_db.py
"""

import csv
import json
import sys
from pathlib import Path

from peewee import fn

# Ensure the project root is on sys.path so that
# "from task_manager_05.app import create_app" works
# regardless of which directory the script is run from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from task_manager_05.app import create_app
from task_manager_05.database import db
from task_manager_05.models import Task


def setup_database():
    """
    Set up database with initial data from CSV

    This function:
    1. Creates a Flask app instance (to initialize the database path)
    2. Drops any existing tables (fresh start)
    3. Creates all tables defined in models.py
    4. Loads task data from CSV file
    5. Converts CSV rows to Task objects
    6. Saves all tasks to the database
    """
    print("Setting up task_manager_05 database...")

    # Create Flask application instance
    # We need this to initialize the database path via db.init()
    app = create_app()

    # Use app_context() so Flask hooks (before_request) can run
    with app.app_context():
        # Connect to the database
        db.connect(reuse_if_open=True)

        # Drop existing tables (fresh start)
        # WARNING: This deletes all data!
        print("Dropping existing tables...")
        db.drop_tables([Task])

        # Create all tables defined in models.py
        print("Creating database tables...")
        db.create_tables([Task])
        print("Created table: task")

        # Determine path to CSV file
        # Go up one directory from this script to find task_manager_04
        csv_path = Path(__file__).parent.parent / "task_manager_04" / "tasks.csv"
        print(f"\nLoading data from {csv_path}...")

        # Check if CSV file exists
        if not csv_path.exists():
            print(f"ERROR: CSV file not found at {csv_path}")
            return

        # Open and read the CSV file
        with open(csv_path, "r", encoding="utf-8") as csv_file:
            # DictReader treats first row as headers
            # Each row becomes a dictionary with column names as keys
            csv_reader = csv.DictReader(csv_file)

            # Process each row from the CSV
            for row in csv_reader:
                # Create a Task record in the database
                # Peewee's Model.create() inserts a new row and returns the instance
                # Note: tags are stored as a JSON string since SQLite
                # doesn't have a native JSON column type
                Task.create(
                    title=row["title"],
                    details=row["details"],
                    is_done=row["is_done"].lower() == "true",
                    assignee=row["assignee"],
                    tags=json.dumps(row["tags"].split("|")),
                )
                print(f"  Created task: {row['title']}")

        # Verify what was saved
        # Peewee uses fn.COUNT() for aggregate queries
        # Task.select(fn.COUNT(Task.id)).scalar() returns the count as an integer
        total_tasks = Task.select(fn.COUNT(Task.id)).scalar()

        completed_tasks = (
            Task.select(fn.COUNT(Task.id)).where(Task.is_done is True).scalar()
        )
        pending_tasks = (
            Task.select(fn.COUNT(Task.id)).where(Task.is_done is False).scalar()
        )

        print("\nDatabase statistics:")
        print(f"  Total tasks: {total_tasks}")
        print(f"  Completed: {completed_tasks}")
        print(f"  Pending: {pending_tasks}")

        print("\nSetup complete! Run the application:")
        print("    uv run python run_05.py")
        print("\nVisit: http://localhost:8080/")

        # Close the database connection
        db.close()


# Only run setup if this script is executed directly
if __name__ == "__main__":
    setup_database()
