"""
Database models for task_manager_05
Defines the Task model using Peewee ORM

This demonstrates:
- Creating a model class that inherits from peewee.Model
- Defining table columns with Peewee field types
- Using Peewee types (AutoField, CharField, TextField, BooleanField)
- Storing JSON data using a TextField with manual serialization
"""

import json

from peewee import AutoField, BooleanField, CharField, Model, TextField

from .database import db


class Task(Model):
    """
    Task model representing a task/todo item in the database

    Attributes:
        id: Unique identifier for the task (primary key, auto-increment)
        title: Short title/summary of the task
        details: Full description of what needs to be done
        is_done: Boolean flag indicating if task is completed
        assignee: Person responsible for the task
        tags: List of tags/categories (stored as JSON text)

    Table name: task
    """

    # Primary key: auto-incrementing integer
    # AutoField is Peewee's auto-incrementing primary key field
    id = AutoField()

    # Title: required string field, max 200 characters
    # CharField is for short text with a max_length
    title = CharField(max_length=200)

    # Details: longer text field for full description
    # TextField has no length limit (unlike CharField)
    details = TextField()

    # Is_done: boolean flag, defaults to False
    # BooleanField stores True/False (1/0 in SQLite)
    is_done = BooleanField(default=False)

    # Assignee: person responsible for the task
    assignee = CharField(max_length=100)

    # Tags: stored as JSON text (list of strings)
    # Peewee does not have a built-in JSON field for SQLite,
    # so we use a TextField and serialize/deserialize manually
    tags = TextField()

    class Meta:
        """
        Model metadata - tells Peewee which database to use
        and what the table should be named.

        In Peewee, every Model needs a Meta class with at least
        the database attribute set.
        """

        database = db
        table_name = "task"

    def get_tags(self):
        """
        Deserialize tags from JSON string to Python list

        Since SQLite doesn't have a native JSON column type,
        we store the tags as a JSON string and convert when needed.

        Returns:
            list: List of tag strings
        """
        return json.loads(self.tags) if self.tags else []

    def set_tags(self, tag_list):
        """
        Serialize a Python list to JSON string for storage

        Args:
            tag_list: List of tag strings to store
        """
        self.tags = json.dumps(tag_list)

    def __repr__(self):
        """
        String representation of the Task object
        Useful for debugging and logging

        Returns:
            str: Readable representation of the task
        """
        return f"<Task {self.id}: {self.title} ({'✓' if self.is_done else '○'})>"

    def to_dict(self):
        """
        Convert Task object to dictionary
        Useful for JSON serialization and template rendering

        Returns:
            dict: Dictionary representation of the task
        """
        return {
            "id": self.id,
            "title": self.title,
            "details": self.details,
            "is_done": self.is_done,
            "assignee": self.assignee,
            "tags": self.get_tags(),
        }
