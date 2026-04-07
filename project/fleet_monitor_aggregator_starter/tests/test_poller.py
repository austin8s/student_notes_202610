"""Test suite for the standalone poller script.

Tests ``poll_server`` and ``poll_all`` using monkeypatch to stub out
``httpx.get`` so no real HTTP requests are made. A temporary SQLite
database is used for each test to isolate side effects.

Note:
    The poller is a plain Python script — not a Flask application. These
    tests initialise the Peewee database directly (no Flask app context)
    and exercise the poller functions in isolation.
"""

from unittest.mock import MagicMock

import httpx
import pytest
from fleet_api.database import db
from fleet_api.models import MetricsSnapshot, ServerRecord
from peewee import SqliteDatabase
from poller import poll_all, poll_server

# ---------------------------------------------------------------------------
# Fake agent response — matches the JSON that agent_api returns
# ---------------------------------------------------------------------------

FAKE_METRICS = {
    "timestamp": "2026-03-30T10:01:00",
    "os_type": "Linux",
    "os_version": "5.15.0",
    "cpu_count": 4,
    "cpu_percent": 12.5,
    "memory": {"total": 8000, "used": 4000, "percent": 50.0},
    "disks": [
        {
            "device": "sda1",
            "mountpoint": "/",
            "fstype": "ext4",
            "total": 10000,
            "used": 5000,
            "free": 5000,
            "percent": 50.0,
        }
    ],
    "network": [
        {
            "name": "eth0",
            "ips": ["192.168.1.2"],
            "bytes_sent_since_last": 100,
            "bytes_recv_since_last": 200,
        }
    ],
}

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def test_db(tmp_path):
    """Creates a temporary SQLite database and initialises it.

    The database file is placed in ``tmp_path`` so it is automatically
    cleaned up after the test.

    Args:
        tmp_path (Path): Built-in pytest fixture providing a temporary
            directory unique to this test invocation.

    Yields:
        SqliteDatabase: The initialised Peewee database.
    """
    db_path = str(tmp_path / "test_poller.db")
    db.init(db_path)
    db.connect()
    db.create_tables([ServerRecord, MetricsSnapshot])
    yield db
    if not db.is_closed():
        db.close()


@pytest.fixture
def sample_server(test_db):
    """Creates a single ServerRecord in the test database.

    Args:
        test_db (SqliteDatabase): Fixture that provides the test database.

    Returns:
        ServerRecord: A server record for ``web-01.bcit.ca``.
    """
    return ServerRecord.create(
        hostname="web-01.bcit.ca",
        agent_url="http://127.0.0.1:5000",
    )


@pytest.fixture
def two_servers(test_db):
    """Creates two ServerRecord instances in the test database.

    Args:
        test_db (SqliteDatabase): Fixture that provides the test database.

    Returns:
        tuple[ServerRecord, ServerRecord]: Two server records.
    """
    server_a = ServerRecord.create(
        hostname="web-01.bcit.ca",
        agent_url="http://127.0.0.1:5000",
    )
    server_b = ServerRecord.create(
        hostname="db-01.bcit.ca",
        agent_url="http://127.0.0.1:5002",
    )
    return server_a, server_b


# ---------------------------------------------------------------------------
# Helper — build a fake httpx.Response
# ---------------------------------------------------------------------------


def _make_fake_response(json_data, status_code=200):
    """Returns a MagicMock that behaves like an httpx.Response.

    Args:
        json_data (dict): The JSON payload to return from ``.json()``.
        status_code (int): The HTTP status code.

    Returns:
        MagicMock: A mock response object.
    """
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data
    response.raise_for_status = MagicMock()
    return response


# ---------------------------------------------------------------------------
# Tests — poll_server
# ---------------------------------------------------------------------------


def test_poll_server_creates_snapshot(sample_server, monkeypatch):
    """Test that poll_server creates a MetricsSnapshot on a successful poll.

    Args:
        sample_server (ServerRecord): Fixture providing a server record.
        monkeypatch (pytest.MonkeyPatch): Built-in pytest fixture.
    """
    fake_response = _make_fake_response(FAKE_METRICS)
    monkeypatch.setattr("httpx.get", lambda url, **kwargs: fake_response)

    poll_server(sample_server)

    snapshots = list(MetricsSnapshot.select())
    assert len(snapshots) == 1
    assert snapshots[0].os_type == "Linux"
    assert snapshots[0].os_version == "5.15.0"
    assert snapshots[0].cpu_count == 4
    assert snapshots[0].cpu_percent == 12.5


def test_poll_server_extracts_memory_fields(sample_server, monkeypatch):
    """Test that poll_server extracts memory_total and memory_used from the
    nested ``memory`` dict returned by the agent.

    Args:
        sample_server (ServerRecord): Fixture providing a server record.
        monkeypatch (pytest.MonkeyPatch): Built-in pytest fixture.
    """
    fake_response = _make_fake_response(FAKE_METRICS)
    monkeypatch.setattr("httpx.get", lambda url, **kwargs: fake_response)

    poll_server(sample_server)

    snapshot = MetricsSnapshot.get()
    assert snapshot.memory_total == 8000
    assert snapshot.memory_used == 4000


def test_poll_server_returns_result_dict(sample_server, monkeypatch):
    """Test that poll_server returns a dict with server_id, hostname, status.

    Args:
        sample_server (ServerRecord): Fixture providing a server record.
        monkeypatch (pytest.MonkeyPatch): Built-in pytest fixture.
    """
    fake_response = _make_fake_response(FAKE_METRICS)
    monkeypatch.setattr("httpx.get", lambda url, **kwargs: fake_response)

    result = poll_server(sample_server)

    assert result["server_id"] == sample_server.id
    assert result["hostname"] == "web-01.bcit.ca"
    assert result["status"] == "online"


def test_poll_server_sets_status_online(sample_server, monkeypatch):
    """Test that poll_server sets server.status to 'online' on success.

    Args:
        sample_server (ServerRecord): Fixture providing a server record.
        monkeypatch (pytest.MonkeyPatch): Built-in pytest fixture.
    """
    fake_response = _make_fake_response(FAKE_METRICS)
    monkeypatch.setattr("httpx.get", lambda url, **kwargs: fake_response)

    assert sample_server.status == "unknown"

    poll_server(sample_server)

    # Reload the server from the database
    server = ServerRecord.get_by_id(sample_server.id)
    assert server.status == "online"


def test_poll_server_calls_correct_url(sample_server, monkeypatch):
    """Test that poll_server requests {agent_url}/api/metrics.

    Args:
        sample_server (ServerRecord): Fixture providing a server record.
        monkeypatch (pytest.MonkeyPatch): Built-in pytest fixture.
    """
    called_urls = []

    def fake_get(url, **kwargs):
        called_urls.append(url)
        return _make_fake_response(FAKE_METRICS)

    monkeypatch.setattr("httpx.get", fake_get)

    poll_server(sample_server)

    assert called_urls == ["http://127.0.0.1:5000/api/metrics"]


def test_poll_server_handles_connection_error(sample_server, monkeypatch):
    """Test that poll_server does not create a snapshot when the agent is
    down, and sets status to 'offline'.

    Args:
        sample_server (ServerRecord): Fixture providing a server record.
        monkeypatch (pytest.MonkeyPatch): Built-in pytest fixture.
    """

    def fake_get(url, **kwargs):
        request = httpx.Request("GET", url)
        raise httpx.ConnectError("Connection refused", request=request)

    monkeypatch.setattr("httpx.get", fake_get)

    result = poll_server(sample_server)

    assert MetricsSnapshot.select().count() == 0
    assert result["status"] == "offline"

    server = ServerRecord.get_by_id(sample_server.id)
    assert server.status == "offline"


def test_poll_server_handles_http_error(sample_server, monkeypatch):
    """Test that poll_server handles a non-200 response gracefully.

    Args:
        sample_server (ServerRecord): Fixture providing a server record.
        monkeypatch (pytest.MonkeyPatch): Built-in pytest fixture.
    """
    fake_response = MagicMock()
    fake_response.status_code = 500
    fake_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server Error",
        request=httpx.Request("GET", "http://127.0.0.1:5000/api/metrics"),
        response=MagicMock(status_code=500),
    )

    monkeypatch.setattr("httpx.get", lambda url, **kwargs: fake_response)

    result = poll_server(sample_server)

    assert MetricsSnapshot.select().count() == 0
    assert result["status"] == "offline"


# ---------------------------------------------------------------------------
# Tests — poll_all
# ---------------------------------------------------------------------------


def test_poll_all_polls_every_server(two_servers, monkeypatch):
    """Test that poll_all creates a snapshot for each server and returns
    a summary dict.

    Args:
        two_servers (tuple): Fixture providing two server records.
        monkeypatch (pytest.MonkeyPatch): Built-in pytest fixture.
    """
    fake_response = _make_fake_response(FAKE_METRICS)
    monkeypatch.setattr("httpx.get", lambda url, **kwargs: fake_response)

    result = poll_all()

    assert MetricsSnapshot.select().count() == 2
    assert result["polled"] == 2
    assert result["online"] == 2
    assert result["offline"] == 0
    assert len(result["results"]) == 2


def test_poll_all_no_servers(test_db, monkeypatch):
    """Test that poll_all returns an empty summary when no servers exist.

    Args:
        test_db (SqliteDatabase): Fixture that provides an empty test database.
        monkeypatch (pytest.MonkeyPatch): Built-in pytest fixture.
    """
    called = []

    def fake_get(url, **kwargs):
        called.append(url)
        return _make_fake_response(FAKE_METRICS)

    monkeypatch.setattr("httpx.get", fake_get)

    result = poll_all()

    assert called == []
    assert MetricsSnapshot.select().count() == 0
    assert result["polled"] == 0


def test_poll_all_partial_failure(two_servers, monkeypatch):
    """Test that poll_all continues when one agent is unreachable.

    The first server's agent responds normally; the second raises a
    connection error. Verifies that one snapshot is still created and
    the summary reflects one online and one offline.

    Args:
        two_servers (tuple): Fixture providing two server records.
        monkeypatch (pytest.MonkeyPatch): Built-in pytest fixture.
    """
    server_a, server_b = two_servers
    call_count = []

    def fake_get(url, **kwargs):
        call_count.append(url)
        if server_b.agent_url in url:
            request = httpx.Request("GET", url)
            raise httpx.ConnectError("Connection refused", request=request)
        return _make_fake_response(FAKE_METRICS)

    monkeypatch.setattr("httpx.get", fake_get)

    result = poll_all()

    assert len(call_count) == 2
    assert MetricsSnapshot.select().count() == 1
    assert result["polled"] == 2
    assert result["online"] == 1
    assert result["offline"] == 1


def test_poll_server_multiple_cycles(sample_server, monkeypatch):
    """Test that polling the same server twice creates two snapshots.

    Args:
        sample_server (ServerRecord): Fixture providing a server record.
        monkeypatch (pytest.MonkeyPatch): Built-in pytest fixture.
    """
    fake_response = _make_fake_response(FAKE_METRICS)
    monkeypatch.setattr("httpx.get", lambda url, **kwargs: fake_response)

    poll_server(sample_server)
    poll_server(sample_server)

    assert MetricsSnapshot.select().count() == 2
