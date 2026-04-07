# Exercise: Building an HTTP Client with `httpx`

## Overview

|                          |                                                                                                                                                                                     |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tools**                | VS Code, `uv` package manager                                                                                                                                                      |
| **Learning Objectives**  | Make HTTP requests with `httpx`, parse JSON responses, send JSON bodies with POST and PUT, handle HTTP errors, use `httpx.Client` for persistent connections                        |

In this exercise you switch sides. You have been building **servers** — now you
write a **client** that talks to one. You will use the `httpx` library to send
HTTP requests, read JSON responses, and handle errors — all from Python code.

A practice server (`server.py`) is provided. It manages a small inventory of
items and **echoes** back what it receives in every write response so you can
verify your requests are correct.

> **Background reading:** Make sure you have read
> `httpx_python_http_clients.md` before starting.

---

## The Practice Server

The provided `server.py` is a Flask API with these endpoints:

| Method   | URL                | Purpose              | Success Code     |
| -------- | ------------------ | -------------------- | ---------------- |
| `GET`    | `/api/status`      | Server health check  | `200`            |
| `GET`    | `/api/items`       | List all items       | `200`            |
| `GET`    | `/api/items/<id>`  | Get one item         | `200` (or `404`) |
| `POST`   | `/api/items`       | Create a new item    | `201`            |
| `PUT`    | `/api/items/<id>`  | Update an item       | `200` (or `404`) |
| `DELETE` | `/api/items/<id>`  | Delete an item       | `200` (or `404`) |

Each item has four fields: `id`, `name`, `category`, and `value`. The server
starts with three pre-seeded items.

Every **write** response (POST, PUT, DELETE) includes an `echo` object that
shows exactly what the server received — the HTTP method, the URL, and the
request body. Use this to confirm your client is sending the right data.

Open `server.py` and skim through it before you begin — the routes, status
codes, and JSON handling should be familiar from your Flask exercise.

---

## Setup (2 minutes)

Open a terminal in the project folder and install the dependencies:

```powershell
uv sync
```

Start the server:

```powershell
uv run python server.py
```

**Leave this terminal open** for the entire exercise. Open a **second terminal**
in VS Code — this is where you will run your client code.

---

## Part 1 — Reading Data with GET (10 minutes)

### Step 1: Health check and list items

Create a file called `client.py`. Start with a health check and then list all
items:

```python
import httpx

# Health check
response = httpx.get("http://localhost:5000/api/status")
print(f"Status code: {response.status_code}")
print(f"Response:    {response.json()}")

# List all items
response = httpx.get("http://localhost:5000/api/items")
items = response.json()

print(f"\nThere are {len(items)} items:")
for item in items:
    print(f"  [{item['id']}] {item['name']} ({item['category']}) = {item['value']}")
```

Run it in your second terminal:

```powershell
uv run python client.py
```

### Step 2: Get a single item

Now write code **on your own** to fetch a single item by its ID. The server
expects the ID in the URL path (check the endpoint table above).

```python
# Get a single item
# TODO: Send a GET request to fetch item 1
# Hint: The URL pattern is /api/items/<id>
#       See "GET — retrieve data" in httpx_python_http_clients.md Section 5
response = ___
item = response.json()
print(f"\nItem 1: {item['name']} — value: {item['value']}")
```

Once it works, change the URL to request **item 99** and run again.

### Q1.1

What status code does the server return for item 99? What key is in
the JSON body instead of `name`?

---

## Part 2 — Writing Data with POST, PUT, and DELETE (15 minutes)

### Step 1: Create a new item with POST

Add code that sends a JSON body to create a new item. Note the `json=`
parameter — this is how `httpx` sends JSON (it handles serialization and
the `Content-Type` header for you):

```python
# Create a new item
new_item = {"name": "Humidity Sensor", "category": "sensor", "value": 45.2}
response = httpx.post("http://localhost:5000/api/items", json=new_item)

print(f"\nPOST status: {response.status_code}")
result = response.json()
print(f"Server says: {result['message']}")
print(f"Created item: {result['item']}")
print(f"Echo: {result['echo']}")
```

### Q2.1

What status code did the POST return? Why is it not `200`? Look at the `echo`
object — what does `body_received` show you?

### Step 2: Update an item with PUT

**Write your own code** to update the item you just created. You need to:

1. Get the `id` of the created item from the POST response (it is inside
   `result["item"]["id"]`)
2. Send a PUT request with a JSON body containing the fields you want to change
3. Print the status code and the updated item from the response

> **Reference:** See "PUT — update data" in `httpx_python_http_clients.md` Section 5.

```python
# Update the item
created_id = result["item"]["id"]

# TODO: Send a PUT request to /api/items/<created_id>
#       with a JSON body that changes the value to 50.0
# Hint: httpx.put(url, json={...})
response = ___

print(f"\nPUT status: {response.status_code}")
put_result = response.json()
print(f"Updated item: {put_result['item']}")
```

### Step 3: Delete an item and confirm

**Write this step entirely on your own.** You need to:

1. Send a DELETE request to remove the item you created (use `created_id`)
2. Print the status code and the server's message
3. Send a GET request for the same item to confirm it is gone
4. Print the status code of that GET

> **Reference:** See "DELETE — remove data" in `httpx_python_http_clients.md`
> Section 5.

```python
# Delete the item
# TODO: Send a DELETE request to /api/items/<created_id>
# TODO: Print the status code and response message

# Confirm deletion
# TODO: Send a GET request for the same item
# TODO: Print the status code — what do you expect it to be?
```

### Q2.2

What status code does the GET return after the item has been deleted?

---

## Part 3 — `httpx.Client` and Error Handling (15 minutes)

So far every request opens a **new connection** and requires the **full URL**.
The `httpx.Client` class solves both problems — it keeps one connection open
and lets you set a `base_url` so you only write relative paths.

In this part you also learn to handle errors, since real APIs can return
unexpected status codes or be completely unreachable.

> **Reference:** See `httpx_python_http_clients.md` Section 7 for `httpx.Client` and
> Section 6 for error handling.

### Step 1: Create a client and read data

Create a new file called `client_v2.py`:

```python
import httpx

client = httpx.Client(base_url="http://localhost:5000", timeout=10.0)

# Health check — notice the relative path (no http://localhost:5000)
status = client.get("/api/status").json()
print(f"Server: {status['status']}, Items: {status['item_count']}")

# TODO: List all items using client.get() with a relative path
#       Print each item's name
```

Run it:

```powershell
uv run python client_v2.py
```

### Q3.1

Compare the URLs in `client_v2.py` with those in `client.py`. What is
different? Why is `httpx.Client` more efficient when making many requests to
the same server?

### Step 2: CRUD with error handling

Now add a full create → update → delete cycle to `client_v2.py`. This time,
use `raise_for_status()` after each request to catch errors automatically.

`raise_for_status()` does nothing on success (2xx) but raises
`httpx.HTTPStatusError` on 4xx or 5xx.

**Write these operations yourself** using the `client` object:

```python
# Create
# TODO: Use client.post() to create an item with:
#       name="Flow Meter", category="sensor", value=3.7
# TODO: Call raise_for_status() on the response
# TODO: Save the new item's id from the response JSON

# Update
# TODO: Use client.put() to change the value to 4.2
# TODO: Call raise_for_status()

# Delete
# TODO: Use client.delete() to remove the item
# TODO: Call raise_for_status()
# TODO: Print the server's confirmation message
```

### Step 3: Handle a missing resource

Add a `try`/`except` block that requests an item that does not exist.
`raise_for_status()` will raise `httpx.HTTPStatusError` — catch it and print
the status code and error message from the server.

```python
# Handle a 404
# TODO: Write a try/except block that:
#   - GETs /api/items/999 using the client
#   - Calls raise_for_status()
#   - Catches httpx.HTTPStatusError
#   - Prints e.response.status_code and e.response.json()["error"]
# Reference: httpx_python_http_clients.md Section 6
```

### Q3.2

What does `raise_for_status()` do when the status code is `200`?
What does it do when the status code is `404`?

### Optional challenge: Handle a connection error

If you finish early: **stop the server** (`Ctrl+C`), then add a
`try`/`except` that catches `httpx.ConnectError` when the server is
unreachable. See `httpx_python_http_clients.md` Section 6 for the pattern.

---

## Reflection

### Q4.1

In your Flask exercise, you built the **server** side. In this
exercise you built the **client** side. In a real system, why might one Python
program need to be both a server (receiving requests) and a client (sending
requests to other servers)?
