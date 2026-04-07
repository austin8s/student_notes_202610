"""Entry point for running the Flask development server.

This script creates the Flask application using the application factory
pattern and starts the built-in development server.  Run it directly::

    python run.py

The ``if __name__`` guard ensures the server only starts when the file
is executed as a script, not when it is imported as a module.
"""

from book_app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
