"""API sub-package.

Registers the ``api`` Blueprint and imports its route definitions.

A Flask *Blueprint* groups related routes together.  All routes in
this package share the ``/api`` URL prefix, so ``/books`` becomes
``/api/books`` in the final application.
"""

from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Import routes after api_bp is defined so the @api_bp.route() decorators work
from . import routes  # noqa: E402, F401
