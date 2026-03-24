"""Database instance for task_manager_07.

Configures a Peewee SqliteDatabase with deferred initialization.
The database path is set later via ``db.init()`` in ``app.py``.
"""

from peewee import SqliteDatabase

db = SqliteDatabase(None)
