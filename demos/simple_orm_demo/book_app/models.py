"""Peewee ORM models for the book application.

Defines ``BaseModel`` (shared database binding) and the ``Book`` model
that maps to the *book* table in SQLite.

In an ORM (Object-Relational Mapper) each Python class corresponds to
a database table, and each instance of that class corresponds to a row.
Peewee uses class attributes (``CharField``, ``BooleanField``, etc.) to
describe the columns of the table.
"""

from peewee import AutoField, BooleanField, CharField, Model

from .database import db


class BaseModel(Model):
    """Base model that binds every subclass to the same database.

    Peewee uses an inner ``Meta`` class to hold configuration.  By
    setting ``database = db`` here, every model that inherits from
    ``BaseModel`` will automatically use our SQLite database without
    repeating the setting.
    """

    class Meta:
        database = db


class Book(BaseModel):
    """ORM model that maps to the ``book`` table in SQLite.

    Each instance represents one row.  Peewee field types map directly
    to SQL column types:

    * ``AutoField``  -> INTEGER PRIMARY KEY AUTOINCREMENT
    * ``CharField``  -> VARCHAR
    * ``BooleanField`` -> BOOLEAN (stored as 0/1 in SQLite)

    Attributes:
        id (AutoField): Auto-incrementing primary key.
        title (CharField): Book title (max 200 characters).
        author (CharField): Author name (max 100 characters).
        is_read (BooleanField): Whether the book has been read.
            Defaults to ``False``.
    """

    class Meta:
        table_name = "book"

    id = AutoField()
    title = CharField(max_length=200)
    author = CharField(max_length=100)
    is_read = BooleanField(default=False)

    def to_dict(self):
        """Convert this model instance to a plain dictionary.

        Flask can serialize a ``dict`` to JSON automatically, but it
        cannot serialize a Peewee ``Model`` instance.  This helper
        bridges that gap.

        Returns:
            dict: A dictionary with keys ``id``, ``title``, ``author``,
            and ``is_read``.
        """
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "is_read": self.is_read,
        }
