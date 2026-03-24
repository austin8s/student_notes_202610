"""
Database configuration and initialization

Peewee ORM Overview:
Peewee is a lightweight Python ORM (Object-Relational Mapping) library.
Unlike Flask-SQLAlchemy, Peewee does not require a Flask extension.
Instead, we create a database instance directly and connect it
to Flask using before_request/teardown_appcontext hooks.

Key Components:
- SqliteDatabase: Manages the connection to a SQLite database file
- Model: Base class that all models inherit from
- Model.Meta.database: Tells each model which database to use
"""

from peewee import SqliteDatabase

# Create a Peewee database instance
# We use None as the initial database path because the actual path
# will be set later in the app factory (create_app) using db.init()
# This is similar to Flask-SQLAlchemy's lazy initialization pattern
db = SqliteDatabase(None)
