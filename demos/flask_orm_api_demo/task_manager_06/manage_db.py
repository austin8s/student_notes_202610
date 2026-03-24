"""
Database setup script for task_manager_06
Creates database with relational tables and populates with initial data from CSV

This script demonstrates:
- Creating multiple related tables (Users, Tasks, Tags)
- Setting up many-to-many relationships (TaskTag through-model)
- Parsing CSV data with relationships
- Bulk inserting related records
- Using Peewee ORM for database operations

Run this before starting the application:
    python task_manager_06/manage_db.py
"""

import csv
import sys
from pathlib import Path

from peewee import fn

# Ensure the project root is on sys.path so that
# "from task_manager_06.app import create_app" works
# regardless of which directory the script is run from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from task_manager_06.app import create_app
from task_manager_06.database import db
from task_manager_06.models import Tag, Task, TaskTag, User


def setup_database():
    """
    Set up relational database with initial data from CSV

    This function:
    1. Creates a Flask app instance (to initialize the database path)
    2. Drops any existing tables (fresh start)
    3. Creates all tables: user, task, tag, and task_tag
    4. Loads data from CSV files
    5. Creates User, Tag, and Task objects with relationships
    6. Saves all records to the database
    """
    print("Setting up task_manager_06 database...")

    # Create Flask application instance (this calls db.init() with the path)
    app = create_app()

    # Use app_context() so Flask hooks are available
    with app.app_context():
        # Drop all existing tables
        # WARNING: This deletes all data!
        print("Dropping existing tables...")
        db.drop_tables([TaskTag, Task, Tag, User], safe=True)

        # Create all tables defined in models.py
        # Order matters: referenced tables must be created before referencing tables
        print("Creating database tables...")
        db.create_tables([User, Tag, Task, TaskTag])
        print("Created tables: user, tag, task, task_tag")

        # Determine path to CSV file
        # The CSV is in task_manager_04 directory
        csv_path = Path(__file__).parent.parent / "task_manager_04" / "tasks.csv"
        print(f"\nLoading data from {csv_path}...")

        # Check if CSV file exists
        if not csv_path.exists():
            print(f"ERROR: CSV file not found at {csv_path}")
            return

        # Dictionaries to track unique users and tags
        # Key: username/tag name, Value: User/Tag object
        users_dict = {}
        tags_dict = {}

        # Lists to store task data with their tag associations
        task_records = []

        # Open and read the CSV file
        with open(csv_path, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)

            # Process each row from the CSV
            for row in csv_reader:
                # Get or create user
                # Each task has an assignee, extract from CSV
                assignee_name = row["assignee"]

                if assignee_name not in users_dict:
                    # Create new user using Model.create()
                    # This inserts a row and returns the model instance
                    email = (
                        assignee_name.lower().replace(", ", ".").replace(" ", "")
                        + "@example.com"
                    )

                    user = User.create(username=assignee_name, email=email)
                    users_dict[assignee_name] = user
                    print(f"  Created user: {assignee_name}")

                # Get or create tags
                # Tags are pipe-separated in CSV: "urgent|work|meeting"
                tag_names = row["tags"].split("|") if row["tags"] else []
                task_tags = []

                for tag_name in tag_names:
                    tag_name = tag_name.strip()  # Remove extra whitespace

                    if tag_name and tag_name not in tags_dict:
                        # Create new tag
                        tag = Tag.create(name=tag_name)
                        tags_dict[tag_name] = tag
                        print(f"  Created tag: {tag_name}")

                    if tag_name:
                        task_tags.append(tags_dict[tag_name])

                # Create task linked to user via assignee foreign key
                task = Task.create(
                    title=row["title"],
                    details=row["details"],
                    is_done=row["is_done"].lower() == "true",
                    assignee=users_dict[assignee_name],
                )

                # Create many-to-many relationships via TaskTag through-model
                # Each TaskTag row links one task to one tag
                for tag in task_tags:
                    TaskTag.create(task=task, tag=tag)

                print(f"  Created task: {row['title']} (assigned to {assignee_name})")

        # Verify what was saved using Peewee aggregate queries
        total_users = User.select(fn.COUNT(User.id)).scalar()
        total_tags = Tag.select(fn.COUNT(Tag.id)).scalar()
        total_tasks = Task.select(fn.COUNT(Task.id)).scalar()
        completed_tasks = (
            Task.select(fn.COUNT(Task.id)).where(Task.is_done is True).scalar()
        )
        pending_tasks = (
            Task.select(fn.COUNT(Task.id)).where(Task.is_done is False).scalar()
        )

        print("\nDatabase statistics:")
        print(f"  Total users: {total_users}")
        print(f"  Total tasks: {total_tasks}")
        print(f"  Total tags: {total_tags}")
        print(f"  Completed tasks: {completed_tasks}")
        print(f"  Pending tasks: {pending_tasks}")

        # Show some relationship examples
        print("\nRelationship examples:")
        first_user = User.select().first()

        if first_user:
            task_count = first_user.tasks.count()
            print(f"  User '{first_user.username}' has {task_count} task(s)")

        first_task = Task.select().first()

        if first_task:
            tag_count = first_task.get_tags().count()
            print(f"  Task '{first_task.title}' has {tag_count} tag(s)")

        print("\nSetup complete! Run the application:")
        print("    uv run python run_06.py")
        print("\nVisit: http://localhost:8080/")


# Only run setup if this script is executed directly
if __name__ == "__main__":
    setup_database()
