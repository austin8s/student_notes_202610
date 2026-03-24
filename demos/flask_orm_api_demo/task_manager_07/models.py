"""Defines all ORM-mapped entities for the task manager demo

Peewee ORM (Object-Relational Mapping) Overview:
ORM allows you to work with database tables as Python classes and rows as Python objects.
Instead of writing SQL queries, you work with Python objects and Peewee generates the SQL.

Key ORM Concepts:
- Model classes represent database tables
- Class attributes (Field instances) represent table columns
- Model instances represent individual rows in the table
- ForeignKeyField creates relationships between tables (foreign keys)
- ManyToManyField or through-models handle many-to-many relationships

Peewee Field Types Summary:
    - AutoField(): Auto-incrementing integer primary key
    - CharField(max_length=N): Short text with maximum length
    - TextField(): Long text with no length limit
    - BooleanField(): True/False values (stored as 1/0 in SQLite)
    - DateTimeField(): Date and time values
    - ForeignKeyField(Model): Creates a foreign key to another model
    - IntegerField(): Integer values

Peewee Query Methods Summary:
This models.py file defines the database structure. To query this data, you use:

1. Model.select():
   - Creates a SELECT query for the model's table
   - Returns a ModelSelect (iterable of model instances)
   - Can be chained with .where(), .order_by(), .limit(), etc.
   - Example: User.select()

2. Model.get_by_id(pk):
   - Fetches a single record by primary key
   - Returns the model instance
   - Raises DoesNotExist if not found
   - Example: User.get_by_id(5)

3. Model.get_or_none(**kwargs):
   - Fetches a single record matching the filter
   - Returns the model instance or None
   - Example: User.get_or_none(User.username == "Alice")

4. Model.select().where(condition):
   - Adds a WHERE clause to filter results
   - Returns filtered ModelSelect
   - Example: Task.select().where(Task.is_done == False)

5. Model.select(fn.COUNT(Model.id)).scalar():
   - Aggregate queries using fn (functions)
   - .scalar() returns a single value
   - Example: Task.select(fn.COUNT(Task.id)).scalar()

Common Query Patterns:
# Get all records:
users = User.select()

# Get one record by primary key:
user = User.get_by_id(5)

# Get one record by other criteria (returns None if not found):
user = User.get_or_none(User.username == "Alice")

# Filter records:
active_tasks = Task.select().where(Task.is_done == False)

# Count records:
from peewee import fn
user_count = User.select(fn.COUNT(User.id)).scalar()
"""

import datetime

from peewee import (
    AutoField,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    Model,
    TextField,
)

from .database import db


class BaseModel(Model):
    """
    Base model class for all database models

    In Peewee, every Model needs a Meta class with the database attribute.
    By creating a BaseModel, we avoid repeating the Meta class in every model.
    All models inherit from BaseModel instead of Model directly.
    """

    class Meta:
        database = db


class User(BaseModel):
    """
    User model representing a person who creates or is assigned tasks

    This class maps to the 'user' table in the database.
    Each instance of this class represents one row in the user table.

    Attributes:
        id: Unique identifier (primary key, auto-increment)
        username: Unique username in format "Lastname, Firstname"
                  where Firstname includes any titles or middle names
                  Examples: "Chen, Sarah", "Mitchell, Dr. Laura", "Watson, Emily Jane"
        email: User's email address (must be unique)
        created_at: Timestamp when user was created

    Relationships:
        - One user can have many tasks (one-to-many)
        - Access via: user.tasks (backref created by ForeignKeyField in Task)

    Database Table:
    CREATE TABLE user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )

    Query Examples:
    # Get all users:
    users = User.select()

    # Get one user by ID:
    user = User.get_by_id(5)

    # Get one user by username:
    user = User.get_or_none(User.username == "Chen, Sarah")

    # Get users ordered by username:
    users = User.select().order_by(User.username)

    # Count users:
    from peewee import fn
    count = User.select(fn.COUNT(User.id)).scalar()

    # Access user's tasks (via backref):
    user = User.get_by_id(5)
    for task in user.tasks:
        print(task.title)
    """

    class Meta:
        table_name = "user"

    # Primary Key Column:
    # AutoField is Peewee's auto-incrementing primary key field
    # It automatically creates an integer column that increments for each new row
    id = AutoField()

    # Unique String Column:
    # CharField(max_length=50) is for short text with a maximum length
    # unique=True: No two users can have the same username
    username = CharField(max_length=50, unique=True)

    # Email Column (same pattern as username):
    # unique=True ensures each email can only be used once
    email = CharField(max_length=100, unique=True)

    # DateTime Column with Default Value:
    # DateTimeField stores date and time values
    # default=datetime.datetime.now: Automatically set to current time on insert
    # Note: We pass the function itself (not called) so it evaluates at insert time
    created_at = DateTimeField(default=datetime.datetime.now)

    def __repr__(self):
        """Return string representation for debugging.

        Returns:
            str: Formatted string like ``<User 5: Chen, Sarah>``.
        """
        return f"<User {self.id}: {self.username}>"

    def to_dict(self):
        """Convert User to dictionary for JSON serialization.

        Returns:
            dict: User data with keys ``id``, ``username``, ``email``,
                ``created_at``, and ``task_count``.
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "task_count": self.tasks.count(),
        }


class Tag(BaseModel):
    """
    Tag model representing a category or label for tasks

    This class maps to the 'tag' table in the database.

    Attributes:
        id: Unique identifier (primary key)
        name: Tag name (e.g., "urgent", "work", "personal") - must be unique

    Relationships:
        - Many tags can be on many tasks (many-to-many via task_tag junction table)

    Database Table:
    CREATE TABLE tag (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) UNIQUE NOT NULL
    )

    Query Examples:
    # Get all tags:
    tags = Tag.select()

    # Get one tag by ID:
    tag = Tag.get_by_id(5)

    # Get one tag by name:
    tag = Tag.get_or_none(Tag.name == "urgent")

    # Get tags ordered alphabetically:
    tags = Tag.select().order_by(Tag.name)

    # Count tags:
    from peewee import fn
    count = Tag.select(fn.COUNT(Tag.id)).scalar()

    # Access tag's tasks (via TaskTag through-model):
    tag = Tag.get_or_none(Tag.name == "urgent")
    tasks = (Task.select()
             .join(TaskTag)
             .where(TaskTag.tag == tag))
    """

    class Meta:
        table_name = "tag"

    # Primary key (same pattern as User.id)
    id = AutoField()

    # Name column: unique string, max 50 characters
    # unique=True: No duplicate tag names allowed
    name = CharField(max_length=50, unique=True)

    def __repr__(self):
        """Return string representation for debugging.

        Returns:
            str: Formatted string like ``<Tag 3: urgent>``.
        """
        return f"<Tag {self.id}: {self.name}>"

    def get_tasks(self):
        """
        Get all tasks that have this tag via the TaskTag junction table.

        This mirrors Task.get_tags() but navigates the relationship
        in the opposite direction (Tag -> Tasks).

        Returns:
            SelectQuery: Query of Task objects with this tag
        """
        return Task.select().join(TaskTag).where(TaskTag.tag == self)


class Task(BaseModel):
    """
    Task model representing a todo item

    This class maps to the 'task' table in the database.

    Attributes:
        id: Unique identifier (primary key)
        title: Short task description
        details: Full task description
        is_done: Completion status (boolean)
        created_at: When task was created
        assignee: Foreign key to User table (creates relationship)

    Relationships:
        - Many tasks belong to one user (many-to-one via ForeignKeyField)
        - Many tasks can have many tags (many-to-many via TaskTag through-model)

    Database Table:
    CREATE TABLE task (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(200) NOT NULL,
        details TEXT NOT NULL,
        is_done BOOLEAN DEFAULT 0 NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        assignee_id INTEGER NOT NULL REFERENCES user(id)
    )

    Foreign Key Explanation:
    assignee is a ForeignKeyField that links to User.
    - Stores an integer (the id of a user) in the assignee_id column
    - Must be a valid user id (referential integrity enforced by database)
    - Creates many-to-one relationship: many tasks -> one user
    - backref="tasks" creates a reverse accessor on User (user.tasks)

    Query Examples:
    # Get all tasks:
    tasks = Task.select()

    # Get one task by ID:
    task = Task.get_by_id(1)

    # Get incomplete tasks:
    tasks = Task.select().where(Task.is_done == False)

    # Get tasks for a specific user:
    tasks = Task.select().where(Task.assignee == user)

    # Get tasks ordered by title:
    tasks = Task.select().order_by(Task.title)

    # Access task's assignee (via foreign key):
    task = Task.get_by_id(1)
    print(task.assignee.username)  # "Chen, Sarah"
    """

    class Meta:
        table_name = "task"

    # Primary key (same pattern as User.id)
    id = AutoField()

    # Title column: required string, max 200 characters
    title = CharField(max_length=200)

    # Details column: TextField for longer content
    # TextField has no length limit (unlike CharField)
    details = TextField()

    # Boolean column with default value
    # BooleanField stores True/False (1/0 in SQLite)
    # default=False: New tasks start as incomplete
    is_done = BooleanField(default=False)

    # DateTime column (same as User.created_at)
    created_at = DateTimeField(default=datetime.datetime.now)

    # Foreign Key Column:
    # ForeignKeyField creates the relationship to User.
    #
    # ForeignKeyField(User, backref="tasks")
    #   * User: The model this field references
    #   * backref="tasks": Creates a reverse accessor on User
    #     - task.assignee gives the User object
    #     - user.tasks gives all Task objects for that user
    #   * column_name="assignee_id": The actual database column name
    #   * on_delete="CASCADE": When a user is deleted, delete their tasks too
    #
    # This creates the SQL constraint:
    # FOREIGN KEY (assignee_id) REFERENCES user(id) ON DELETE CASCADE
    #
    # Usage:
    #   task = Task.get_by_id(1)
    #   task.assignee        # User object
    #   task.assignee_id     # Just the integer ID
    #   task.assignee.username  # "Chen, Sarah"
    assignee = ForeignKeyField(
        User, backref="tasks", column_name="assignee_id", on_delete="CASCADE"
    )

    def __repr__(self):
        """Return string representation with completion status.

        Returns:
            str: Formatted string like ``<Task 1: Learn Flask (✓)>``.
        """
        status = "✓" if self.is_done else "○"
        return f"<Task {self.id}: {self.title} ({status})>"

    def to_dict(self):
        """Convert Task to dictionary for JSON serialization.

        Returns:
            dict: Task data with keys ``id``, ``title``, ``details``,
                ``is_done``, ``created_at``, ``assignee``, ``assignee_id``,
                and ``tags``.
        """
        return {
            "id": self.id,
            "title": self.title,
            "details": self.details,
            "is_done": self.is_done,
            "created_at": self.created_at.isoformat(),
            "assignee": self.assignee.username,
            "assignee_id": self.assignee_id,
            "tags": [tag.name for tag in self.get_tags()],
        }

    def get_tags(self):
        """
        Get all tags associated with this task via the TaskTag junction table.

        In Peewee, many-to-many relationships are navigated by querying
        through the junction/through-model.

        Returns:
            SelectQuery: Query of Tag objects for this task
        """
        return Tag.select().join(TaskTag).where(TaskTag.task == self)

    def get_tag_ids(self):
        """
        Get the IDs of all tags associated with this task.

        Useful for pre-selecting checkboxes in edit forms.

        Returns:
            list[int]: List of tag IDs for this task
        """
        return [tag.id for tag in self.get_tags()]


class TaskTag(BaseModel):
    """
    Junction/Association table for the Many-to-Many relationship
    between Tasks and Tags.

    This table links Tasks and Tags together:
    - A Task can have many Tags (e.g., "Fix bug" has tags: urgent, backend, bug)
    - A Tag can be on many Tasks (e.g., "urgent" tag on multiple tasks)

    In Peewee, many-to-many relationships use a "through model" (this class)
    instead of an implicit association table.

    This creates a SQL table like:
    CREATE TABLE task_tag (
        id INTEGER PRIMARY KEY,
        task_id INTEGER REFERENCES task(id),
        tag_id INTEGER REFERENCES tag(id),
        UNIQUE (task_id, tag_id)
    )

    Example data:
    | task_id | tag_id |  Meaning
    |---------|--------|----------------------------------
    | 1       | 5      |  Task 1 has Tag 5
    | 1       | 7      |  Task 1 also has Tag 7
    | 2       | 5      |  Task 2 has Tag 5
    | 3       | 7      |  Task 3 has Tag 7

    How to query:
    # Get all tags for a task:
    tags = Tag.select().join(TaskTag).where(TaskTag.task == task)

    # Get all tasks with a tag:
    tasks = Task.select().join(TaskTag).where(TaskTag.tag == tag)

    # Add a tag to a task:
    TaskTag.create(task=task, tag=tag)

    # Remove a tag from a task:
    TaskTag.delete().where((TaskTag.task == task) & (TaskTag.tag == tag)).execute()

    # Remove all tags from a task:
    TaskTag.delete().where(TaskTag.task == task).execute()
    """

    class Meta:
        table_name = "task_tag"
        # Ensure each task-tag pair is unique (composite unique constraint)
        indexes = ((("task", "tag"), True),)  # True means unique

    # Foreign key to Task table
    task = ForeignKeyField(Task, backref="task_tags", on_delete="CASCADE")

    # Foreign key to Tag table
    tag = ForeignKeyField(Tag, backref="task_tags", on_delete="CASCADE")


def get_tasks_for_tag(tag):
    """
    Helper function: Get all tasks that have a specific tag.

    Navigates the many-to-many relationship from Tag -> Tasks
    through the TaskTag junction table.

    Args:
        tag: Tag model instance

    Returns:
        SelectQuery: Query of Task objects with this tag
    """
    return Task.select().join(TaskTag).where(TaskTag.tag == tag)


"""
CRUD Operations with Peewee:

CREATE:
    # Create a new record (inserts immediately):
    user = User.create(username="Alice", email="alice@example.com")

    # Or create without saving, then save:
    user = User(username="Alice", email="alice@example.com")
    user.save()

READ:
    # Get all records:
    users = User.select()

    # Get one record by primary key:
    user = User.get_by_id(5)

    # Get one record safely:
    user = User.get_or_none(User.username == "Alice")

    # Filter records:
    tasks = Task.select().where(Task.is_done == False)

UPDATE:
    # Update a single record:
    user = User.get_by_id(5)
    user.username = "New Name"
    user.save()

    # Bulk update:
    User.update(email="new@example.com").where(User.id == 5).execute()

DELETE:
    # Delete a single record:
    user = User.get_by_id(5)
    user.delete_instance()

    # Bulk delete:
    User.delete().where(User.id == 5).execute()

MANY-TO-MANY:
    # Add tag to task:
    TaskTag.create(task=task, tag=tag)

    # Remove all tags from task:
    TaskTag.delete().where(TaskTag.task == task).execute()

    # Replace tags (delete old, add new):
    TaskTag.delete().where(TaskTag.task == task).execute()
    for tag in new_tags:
        TaskTag.create(task=task, tag=tag)
"""
