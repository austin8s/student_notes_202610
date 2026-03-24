# Exercise: Building Your First Flask API

## Overview

| | |
|---|---|
| **Tools** | VS Code, `uv` package manager, `curl`, optionally Bruno |
| **Prerequisites** | Python basics, HTTP & REST concepts (`http_review.md`), Flask overview (`flask_intro.md`, `wsgi_overview.md`) |
| **Learning Objectives** | Create a Flask application, define routes and view functions, return JSON responses, accept JSON input, organize code with blueprints |

In this exercise you will build a Flask JSON API from scratch — starting with
the simplest possible application and progressively restructuring it into a
modular project using the **application factory pattern** and **blueprints**.

By the end you will have a working API that you can test with `curl` (or
Bruno), and you will understand the project structure used in real Flask
applications.

> **Background reading:** Before starting, make sure you have read
> [http_review.md](),
> [flask_intro.md](), and
> [wsgi_overview.md]().
> The [Bruno & curl exercise]()
> gives you hands-on experience with HTTP requests and responses that you will
> build on here.

---

## The Domain: A Bookshelf API

You will build a small **Bookshelf API** that manages a collection of books
stored in an in-memory Python list. The API will support:

- Listing all books
- Retrieving a single book by ID
- Adding a new book
- Deleting a book

This is intentionally simple — no database, no ORM, no authentication. The
focus is on learning Flask's core patterns.

---

## Part 1 — Hello Flask (25 minutes)

### Step 1: Create the project

Open a terminal and create a new project using `uv`:

```powershell
# Create a new directory and navigate into it
mkdir bookshelf_api
cd bookshelf_api

# Initialize a Python project with uv
uv init

# Add Flask as a dependency
uv add flask
```

**Q1.1:** Open `pyproject.toml`. What did `uv init` create? What did
`uv add flask` add to the file?

### Step 2: Write a single-file Flask app

Create a file called `app.py` in the `bookshelf_api` folder with the following
content:

```python
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return {"message": "Welcome to the Bookshelf API"}


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
```

**Q1.2:** In your own words, explain what each of these lines does:

a) `app = Flask(__name__)`

b) `@app.route("/")`

c) `return {"message": "Welcome to the Bookshelf API"}`

d) `app.run(host="localhost", port=5000, debug=True)`

### Step 3: Run the server and test it

Start the development server:

```powershell
uv run python app.py
```

You should see output similar to:

```
 * Running on http://localhost:5000
 * Restarting with stat
 * Debugger is active!
```

Open a **second terminal** and test the endpoint with `curl`:

```powershell
curl http://localhost:5000/
```

**Q1.3:** What does the response look like? What `Content-Type` header does
Flask set when you return a Python dictionary?

### Step 4: Add more routes

Add these two routes to `app.py` (above the `if __name__` block):

```python
@app.route("/about")
def about():
    return {
        "app": "Bookshelf API",
        "version": "1.0.0",
        "description": "A simple API to manage a book collection",
    }


@app.route("/status")
def status():
    return {"status": "running", "debug": True}
```

Because you started the server with `debug=True`, it should **auto-reload**
when you save the file. Test both new endpoints:

```powershell
curl http://localhost:5000/about
curl http://localhost:5000/status
```

**Q1.4:** Did you need to restart the server after adding the new routes?
Why or why not? (Hint: see `wsgi_overview.md` §3.)

### Step 5: Add book data and a list endpoint

Add an in-memory book collection and a route that returns it. Place the list
near the top of `app.py` (after the `app = Flask(__name__)` line) and add the
route:

```python
from flask import Flask, jsonify

# In-memory data store
books = [
    {"id": 1, "title": "Python Crash Course", "author": "Eric Matthes"},
    {"id": 2, "title": "Automate the Boring Stuff", "author": "Al Sweigart"},
    {"id": 3, "title": "Flask Web Development", "author": "Miguel Grinberg"},
]

# ... existing routes ...


@app.route("/books")
def list_books():
    return jsonify(books)
```

Test it:

```powershell
curl http://localhost:5000/books
```

**Q1.5:** Why do we use `jsonify(books)` here instead of just `return books`?
(Hint: `books` is a list, not a dictionary.)

### Step 6: Add a route for a single book

Add a route that returns a single book by its ID. This uses a **URL variable**
(`<int:book_id>`) to capture part of the URL as a function parameter:

```python
@app.route("/books/<int:book_id>")
def get_book(book_id):
    for book in books:
        if book["id"] == book_id:
            return book
    return {"error": f"Book {book_id} not found"}, 404
```

Test both a valid and invalid ID:

```powershell
curl http://localhost:5000/books/1
curl http://localhost:5000/books/99
```

**Q1.6:**

a) What status code does the second request return? Why?

b) What does `<int:book_id>` do in the route decorator?

---

## Part 2 — Accepting Data with POST and DELETE (20 minutes)

So far every route uses the default `GET` method. Now you will add routes that
**modify** data using `POST` and `DELETE`.

### Step 1: Add a POST route to create a book

Add the following to `app.py`:

```python
from flask import Flask, jsonify, request


@app.route("/books", methods=["POST"])
def create_book():
    data = request.get_json()

    if not data:
        return {"error": "Request body must be JSON"}, 400

    title = data.get("title")
    author = data.get("author")

    if not title or not author:
        return {"error": "title and author are required"}, 400

    new_id = max(book["id"] for book in books) + 1 if books else 1
    new_book = {"id": new_id, "title": title, "author": author}
    books.append(new_book)

    return new_book, 201
```

Test it with `curl`:

```powershell
curl -X POST http://localhost:5000/books `
  -H "Content-Type: application/json" `
  -d '{"title": "Learning Python", "author": "Mark Lutz"}'
```

Then verify the book was added:

```powershell
curl http://localhost:5000/books
```

**Q2.1:**

a) What does `request.get_json()` do?

b) Why do we return status code `201` instead of `200`?

c) What happens if you send the POST request without the `Content-Type` header?
   Try it:

```powershell
curl -X POST http://localhost:5000/books -d '{"title": "Test", "author": "Test"}'
```

### Step 2: Add a DELETE route

Add this route to `app.py`:

```python
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    for i, book in enumerate(books):
        if book["id"] == book_id:
            deleted = books.pop(i)
            return {"message": f"'{deleted['title']}' deleted successfully"}
    return {"error": f"Book {book_id} not found"}, 404
```

Test deleting a book:

```powershell
curl -X DELETE http://localhost:5000/books/2
curl http://localhost:5000/books
```

**Q2.2:** After deleting book 2, how many books does `GET /books` return?
Is the deleted book still in the list?

### Step 3: Quick checkpoint

At this point your single-file `app.py` should have:

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Welcome message |
| `/about` | GET | App information |
| `/status` | GET | Server status |
| `/books` | GET | List all books |
| `/books/<id>` | GET | Get one book |
| `/books` | POST | Add a book |
| `/books/<id>` | DELETE | Remove a book |

Test all of them to make sure everything works before continuing.

**Q2.3:** Look at the terminal where your Flask server is running. What
information does the server log for each request?

---

## Part 3 — Application Factory and Blueprints (30 minutes)

Your single-file app works, but real projects split code into multiple files.
In this part you will **restructure** the same Bookshelf API into a modular
layout using Flask's **application factory pattern** and **blueprints**.

> **Reference:** See the "Project Layouts" section of `flask_intro.md` for
> an overview of how these concepts map to files.

### Target structure

When you are done, your project will look like this:

```text
bookshelf_api/
├── bookshelf/
│   ├── __init__.py          # Application factory (create_app)
│   └── routes/
│       ├── __init__.py      # Empty — makes routes/ a package
│       ├── home.py          # Home blueprint (/, /about, /status)
│       └── books.py         # Books blueprint (/books, /books/<id>)
├── run.py                   # Entry script
└── pyproject.toml           # Project config
```

### Step 1: Create the package structure

**Stop the running server** (`Ctrl+C`), then create the directories and files:

```powershell
mkdir bookshelf
mkdir bookshelf/routes
```

Create the following files. You can create empty files in VS Code or use the
terminal.

### Step 2: Create the home blueprint — `bookshelf/routes/home.py`

Move the home-related routes into a blueprint:

```python
from flask import Blueprint

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home():
    return {"message": "Welcome to the Bookshelf API"}


@home_bp.route("/about")
def about():
    return {
        "app": "Bookshelf API",
        "version": "1.0.0",
        "description": "A simple API to manage a book collection",
    }


@home_bp.route("/status")
def status():
    return {"status": "running"}
```

**Q3.1:** Compare `@home_bp.route("/")` with `@app.route("/")` from Part 1.
What object are we attaching the route to now, and why?

### Step 3: Create the books blueprint — `bookshelf/routes/books.py`

Move the book-related routes into a separate blueprint. Notice the
`url_prefix` parameter:

```python
from flask import Blueprint, jsonify, request

books_bp = Blueprint("books", __name__, url_prefix="/books")

# In-memory data store
books = [
    {"id": 1, "title": "Python Crash Course", "author": "Eric Matthes"},
    {"id": 2, "title": "Automate the Boring Stuff", "author": "Al Sweigart"},
    {"id": 3, "title": "Flask Web Development", "author": "Miguel Grinberg"},
]


@books_bp.route("/", methods=["GET"])
def list_books():
    return jsonify(books)


@books_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    for book in books:
        if book["id"] == book_id:
            return book
    return {"error": f"Book {book_id} not found"}, 404


@books_bp.route("/", methods=["POST"])
def create_book():
    data = request.get_json()

    if not data:
        return {"error": "Request body must be JSON"}, 400

    title = data.get("title")
    author = data.get("author")

    if not title or not author:
        return {"error": "title and author are required"}, 400

    new_id = max(book["id"] for book in books) + 1 if books else 1
    new_book = {"id": new_id, "title": title, "author": author}
    books.append(new_book)

    return new_book, 201


@books_bp.route("/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    for i, book in enumerate(books):
        if book["id"] == book_id:
            deleted = books.pop(i)
            return {"message": f"'{deleted['title']}' deleted successfully"}
    return {"error": f"Book {book_id} not found"}, 404
```

**Q3.2:**

a) The `books_bp` blueprint is created with `url_prefix="/books"`. What does
   this mean for the route `@books_bp.route("/")`? What URL will it respond to?

b) Why is it useful to set `url_prefix` on a blueprint instead of writing
   `/books` in every route decorator?

### Step 4: Create the `__init__.py` files

Create the package initializer files:

**`bookshelf/routes/__init__.py`** — leave this file empty. It tells Python
that `routes/` is a package.

**`bookshelf/__init__.py`** — this is the application factory:

```python
from flask import Flask


def create_app():
    app = Flask(__name__)

    from .routes.home import home_bp
    from .routes.books import books_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(books_bp)

    return app
```

**Q3.3:**

a) What does `create_app()` return?

b) What does `app.register_blueprint(home_bp)` do?

c) Why are the `import` statements inside the function instead of at the top
   of the file?

### Step 5: Create the entry script — `run.py`

Create `run.py` in the **project root** (not inside `bookshelf/`):

```python
from bookshelf import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
```

### Step 6: Run and test

Start the restructured application:

```powershell
uv run python run.py
```

Test every endpoint to confirm nothing broke:

```powershell
# Home routes
curl http://localhost:5000/
curl http://localhost:5000/about
curl http://localhost:5000/status

# Book routes
curl http://localhost:5000/books
curl http://localhost:5000/books/1

# Create a book
curl -X POST http://localhost:5000/books `
  -H "Content-Type: application/json" `
  -d '{"title": "Fluent Python", "author": "Luciano Ramalho"}'

# Delete a book
curl -X DELETE http://localhost:5000/books/2
```

**Q3.4:** All the URLs are exactly the same as in Part 2. From the client's
perspective, did anything change? Why is this important?

### Step 7: Delete the old `app.py`

Now that the modular version is working, you can delete the original
single-file `app.py`. The `bookshelf/` package is your application now.

---

## Part 4 — Reflection and Looking Ahead (15 minutes)

Answer the following questions in your own words.

**Q4.1: Single file vs. blueprints**

You built the same API twice — once in a single file and once with blueprints.
List two advantages of the blueprint approach.

**Q4.2: Application factory**

Why is `create_app()` a function instead of just creating the `app` object at
module level? (Hint: think about testing and configuration.)

**Q4.3: JSON responses**

In this exercise, when can you return a plain Python dictionary from a view
function, and when do you need `jsonify()`?

**Q4.4: HTTP method and status code review**

Fill in the table with the HTTP method and expected success status code for
each operation your API performs:

| Operation | Route | Method | Success Code |
|-----------|-------|--------|--------------|
| List all books | `/books` | ___ | ___ |
| Get one book | `/books/1` | ___ | ___ |
| Add a book | `/books` | ___ | ___ |
| Delete a book | `/books/1` | ___ | ___ |

**Q4.5: Tracing a request**

Using what you learned in `wsgi_overview.md`, describe the journey of a
`GET /books/1` request from the client to your view function and back. Name
each layer the request passes through.

---

## Summary

| Concept | What you practiced |
|---------|--------------------|
| `Flask(__name__)` | Creating a Flask application instance |
| `@app.route()` | Mapping URLs to view functions |
| Returning `dict` | Automatic JSON serialization |
| `jsonify()` | Serializing lists to JSON |
| `request.get_json()` | Parsing JSON from POST request bodies |
| HTTP status codes | Returning `201`, `400`, `404` |
| `Blueprint` | Organizing routes into modules |
| `url_prefix` | Grouping related routes under a common path |
| `create_app()` | Application factory pattern |
| `run.py` | Entry script pattern |

---

## References

- [Flask Quickstart](https://flask.palletsprojects.com/en/stable/quickstart/)
- [Flask Blueprints](https://flask.palletsprojects.com/en/stable/blueprints/)
- [Flask API — jsonify](https://flask.palletsprojects.com/en/stable/api/#flask.json.jsonify)
- [flask_intro.md](../notes/flask_intro.md) — Flask concepts overview
- [wsgi_overview.md](../../web_http_general/notes/wsgi_overview.md) — How Flask runs your application
- [http_review.md](../../web_http_general/notes/http_review.md) — HTTP and RESTful APIs
- [curl manual](https://curl.se/docs/manpage.html)
