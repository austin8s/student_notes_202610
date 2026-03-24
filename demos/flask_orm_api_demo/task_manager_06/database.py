"""
Sets up the Peewee database instance for task_manager_06

This module configures Peewee, a lightweight Python ORM.
Unlike Flask-SQLAlchemy, Peewee does not require a Flask extension.
Instead, we create a database instance directly and manage connections
using Flask's before_request/teardown_appcontext hooks.

Key Components:
- SqliteDatabase: Manages the connection to a SQLite database file
- Model: Base class that all models inherit from
- Model.Meta.database: Tells each model which database to use

What is Peewee?
Peewee is a small, expressive ORM that simplifies database operations:
- Models map Python classes to database tables
- Fields map class attributes to table columns
- Queries are built with a Pythonic API (Model.select(), .where(), etc.)
- Supports SQLite, PostgreSQL, and MySQL
"""

from peewee import SqliteDatabase

# Create a Peewee database instance
# We use None as the initial database path because the actual path
# will be set later in the app factory (create_app) using db.init()
# This is similar to a lazy initialization pattern
db = SqliteDatabase(None)

"""
How to use the 'db' object:

1. Define models by inheriting from db.Model:
   class User(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       username = db.Column(db.String(50))

2. Query the database using db.session:
   users = db.session.execute(select(User)).scalars().all()
   user = db.session.get(User, 1)

3. Create/update records:
   new_user = User(username="Alice")
   db.session.add(new_user)
   db.session.commit()

4. Initialize with Flask app (in app.py):
   db.init_app(app)
"""
