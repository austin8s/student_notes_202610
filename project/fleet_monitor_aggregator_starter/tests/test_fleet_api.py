"""Test suite for fleet_api Flask routes.

Tests the aggregation server endpoints for server registration, listing,
metric retrieval, and on-demand polling.

Note:
    Unlike the agent tests, these tests do not need ``mock_psutil`` — the
    fleet API does not call psutil directly. Instead, it stores metrics
    received from agents in a database. Tests use a temporary SQLite
    database created via ``tmp_path`` and monkeypatch the poller functions
    to avoid real HTTP calls.
"""

import pytest
from fleet_api import create_app
from fleet_api.database import db
from fleet_api.models import MetricsSnapshot, ServerRecord

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fleet_app(tmp_path):
    """Creates a Flask application backed by a temporary SQLite database.

    Uses ``tmp_path`` (a built-in pytest fixture) to place the database
    file in a directory that is automatically cleaned up after the test.

    Args:
        tmp_path (Path): Built-in pytest fixture providing a temporary
            directory unique to this test invocation.

    Returns:
        Flask: A configured Flask application for testing.
    """
    db_path = str(tmp_path / "test_fleet.db")
    app = create_app(db_path=db_path)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(fleet_app):
    """Creates a Flask test client for the fleet API.

    Args:
        fleet_app (Flask): Fixture defined above that provides a Flask
            application with a temporary database.

    Returns:
        FlaskClient: A test client for the fleet API.
    """
    with fleet_app.test_client() as test_client:
        yield test_client


@pytest.fixture
def registered_server(client):
    """Registers a sample server and returns its JSON representation.

    This is a convenience fixture so that tests which need a server
    already in the database don't have to repeat the POST call.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.

    Returns:
        dict: The JSON response from registering the server.
    """
    response = client.post(
        "/fleet/servers",
        json={"hostname": "web-01.bcit.ca", "agent_url": "http://127.0.0.1:5000"},
    )
    return response.get_json()


# ---------------------------------------------------------------------------
# Tests — Health Check
# ---------------------------------------------------------------------------


def test_status(client):
    """Test that GET /fleet/status returns a health check response.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
    """
    response = client.get("/fleet/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"status": "ok"}


# ---------------------------------------------------------------------------
# Tests — Server Registration
# ---------------------------------------------------------------------------


def test_register_server(client):
    """Test that POST /fleet/servers creates a new server record.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
    """
    response = client.post(
        "/fleet/servers",
        json={"hostname": "web-01.bcit.ca", "agent_url": "http://127.0.0.1:5000"},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["hostname"] == "web-01.bcit.ca"
    assert data["agent_url"] == "http://127.0.0.1:5000"
    assert data["status"] == "unknown"
    assert "id" in data
    assert "created_at" in data


def test_register_server_missing_hostname(client):
    """Test that POST /fleet/servers returns 400 when hostname is missing.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
    """
    response = client.post(
        "/fleet/servers",
        json={"agent_url": "http://127.0.0.1:5000"},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "hostname" in data["error"]


def test_register_server_missing_agent_url(client):
    """Test that POST /fleet/servers returns 400 when agent_url is missing.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
    """
    response = client.post(
        "/fleet/servers",
        json={"hostname": "web-01.bcit.ca"},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "agent_url" in data["error"]


def test_register_server_empty_body(client):
    """Test that POST /fleet/servers returns 400 when no JSON body is sent.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
    """
    response = client.post("/fleet/servers", content_type="application/json")
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Tests — Server Listing
# ---------------------------------------------------------------------------


def test_get_servers_empty(client):
    """Test that GET /fleet/servers returns an empty list initially.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
    """
    response = client.get("/fleet/servers")
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_servers(client, registered_server):
    """Test that GET /fleet/servers returns all registered servers.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
        registered_server (dict): Fixture that has already registered a server.
    """
    response = client.get("/fleet/servers")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["hostname"] == "web-01.bcit.ca"


def test_get_servers_multiple(client):
    """Test that GET /fleet/servers returns multiple servers.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
    """
    client.post(
        "/fleet/servers",
        json={"hostname": "web-01.bcit.ca", "agent_url": "http://127.0.0.1:5000"},
    )
    client.post(
        "/fleet/servers",
        json={"hostname": "db-01.bcit.ca", "agent_url": "http://127.0.0.1:5002"},
    )
    response = client.get("/fleet/servers")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    hostnames = {s["hostname"] for s in data}
    assert hostnames == {"web-01.bcit.ca", "db-01.bcit.ca"}


# ---------------------------------------------------------------------------
# Tests — Server Detail
# ---------------------------------------------------------------------------


def test_get_server_by_id(client, registered_server):
    """Test that GET /fleet/servers/<id> returns the correct server.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
        registered_server (dict): Fixture that has already registered a server.
    """
    server_id = registered_server["id"]
    response = client.get(f"/fleet/servers/{server_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["hostname"] == "web-01.bcit.ca"
    assert data["agent_url"] == "http://127.0.0.1:5000"


def test_get_server_not_found(client):
    """Test that GET /fleet/servers/<id> returns 404 for a non-existent ID.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
    """
    response = client.get("/fleet/servers/999")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


# ---------------------------------------------------------------------------
# Tests — Metrics
# ---------------------------------------------------------------------------


def test_get_metrics_empty(client, registered_server):
    """Test that GET /fleet/servers/<id>/metrics returns an empty list.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
        registered_server (dict): Fixture that has already registered a server.
    """
    server_id = registered_server["id"]
    response = client.get(f"/fleet/servers/{server_id}/metrics")
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_metrics_server_not_found(client):
    """Test that GET /fleet/servers/<id>/metrics returns 404.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
    """
    response = client.get("/fleet/servers/999/metrics")
    assert response.status_code == 404


def test_get_latest_metrics_server_not_found(client):
    """Test that GET /fleet/servers/<id>/metrics/latest returns 404.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
    """
    response = client.get("/fleet/servers/999/metrics/latest")
    assert response.status_code == 404


def test_get_latest_metrics_no_snapshots(client, registered_server):
    """Test that GET /fleet/servers/<id>/metrics/latest returns 404 when
    the server exists but has no snapshots.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
        registered_server (dict): Fixture that has already registered a server.
    """
    server_id = registered_server["id"]
    response = client.get(f"/fleet/servers/{server_id}/metrics/latest")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    assert "No metrics recorded yet" in data["error"]


# ---------------------------------------------------------------------------
# Tests — Poll Endpoints
# ---------------------------------------------------------------------------


def test_poll_all_servers(client, registered_server, monkeypatch):
    """Test that POST /fleet/poll calls poll_all and returns a summary.

    Monkeypatches ``poll_all`` on the routes module so no real HTTP
    requests are made to agents.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
        registered_server (dict): Fixture that has already registered a server.
        monkeypatch (pytest.MonkeyPatch): Built-in pytest fixture used to
            replace the imported ``poll_all`` in the routes module.
    """

    def fake_poll_all():
        return {
            "polled": 1,
            "online": 1,
            "offline": 0,
            "results": [
                {
                    "server_id": registered_server["id"],
                    "hostname": "web-01.bcit.ca",
                    "status": "online",
                }
            ],
        }

    monkeypatch.setattr("fleet_api.api.routes.poll_all", fake_poll_all)
    response = client.post("/fleet/poll")
    assert response.status_code == 200
    data = response.get_json()
    assert data["polled"] == 1
    assert data["online"] == 1
    assert "results" in data


def test_poll_single_server(client, registered_server, monkeypatch):
    """Test that POST /fleet/servers/<id>/poll calls poll_server and returns
    the result dict.

    Monkeypatches ``poll_server`` on the routes module so no real HTTP
    requests are made to agents.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
        registered_server (dict): Fixture that has already registered a server.
        monkeypatch (pytest.MonkeyPatch): Built-in pytest fixture used to
            replace the imported ``poll_server`` in the routes module.
    """

    def fake_poll_server(server):
        return {
            "server_id": server.id,
            "hostname": server.hostname,
            "status": "online",
        }

    monkeypatch.setattr("fleet_api.api.routes.poll_server", fake_poll_server)
    server_id = registered_server["id"]
    response = client.post(f"/fleet/servers/{server_id}/poll")
    assert response.status_code == 200
    data = response.get_json()
    assert data["server_id"] == server_id
    assert data["hostname"] == "web-01.bcit.ca"
    assert data["status"] == "online"


def test_poll_single_server_not_found(client):
    """Test that POST /fleet/servers/<id>/poll returns 404 for a non-existent ID.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
    """
    response = client.post("/fleet/servers/999/poll")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Tests — Invalid Route
# ---------------------------------------------------------------------------


def test_invalid_route(client):
    """Test that a non-existent route returns 404.

    Args:
        client (FlaskClient): Fixture providing the Flask test client.
    """
    response = client.get("/fleet/nonexistent")
    assert response.status_code == 404
