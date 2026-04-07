"""Database configuration module.

Exposes a deferred ``SqliteDatabase`` instance that is initialized at
runtime inside the application factory.

Peewee lets you create a database object with ``None`` as the path.
This is called a *deferred* database — it acts as a placeholder until
you call ``db.init(path)`` later.  We do this so every model file can
import ``db`` at the top level without needing to know the database
path at import time.
"""

from peewee import SqliteDatabase

# None = deferred — the real path is set in create_app() via db.init(...)
db = SqliteDatabase(None)
