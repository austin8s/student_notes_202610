"""Shared fixtures and stub classes for all test modules.

This file is named conftest.py, which is a special filename recognized by
pytest. Any fixtures defined here are automatically available to every test
file in this directory — you do not need to import them. pytest discovers
and loads conftest.py before running tests.

All psutil and platform system calls are replaced with simple stub classes
using monkeypatch, so tests are deterministic and do not depend on real
system information.
"""

import pytest

# ---------------------------------------------------------------------------
# Stub classes — simple stand-ins for psutil objects
# ---------------------------------------------------------------------------


class FakeVirtualMemory:
    """Stub for psutil.virtual_memory() return value."""

    total = 8000
    used = 4000
    percent = 50.0


class FakeDiskPartition:
    """Stub for a single psutil.disk_partitions() entry."""

    device = "sda1"
    mountpoint = "/"
    fstype = "ext4"


class FakeDiskUsage:
    """Stub for psutil.disk_usage() return value."""

    total = 10000
    used = 5000
    free = 5000
    percent = 50.0


class FakeAddress:
    """Stub for a single psutil network interface address."""

    class FakeFamily:
        """Stub for the address family enum."""

        name = "AF_INET"

    family = FakeFamily()
    address = "192.168.1.2"


class FakeIOCounters:
    """Stub for psutil per-NIC IO counters."""

    def __init__(self, bytes_sent, bytes_recv):
        """Initializes FakeIOCounters with sent and received byte counts.

        Args:
            bytes_sent (int): Number of bytes sent.
            bytes_recv (int): Number of bytes received.
        """
        self.bytes_sent = bytes_sent
        self.bytes_recv = bytes_recv


class FakeProcessInfo:
    """Stub for psutil process info dictionary."""

    def __init__(self, name, pid):
        """Initializes FakeProcessInfo.

        Args:
            name: Process name.
            pid: Process ID.
        """
        self.info = {"name": name, "pid": pid}


class FakeConnectionLaddr:
    """Stub for local address of a connection."""

    def __init__(self, ip, port):
        """Initializes FakeConnectionLaddr.

        Args:
            ip: IP address string.
            port: Port number.
        """
        self.ip = ip
        self.port = port


class FakeConnection:
    """Stub for psutil network connection."""

    def __init__(self, ip, port, status):
        """Initializes FakeConnection.

        Args:
            ip: IP address string.
            port: Port number.
            status: Connection status string.
        """
        self.laddr = FakeConnectionLaddr(ip, port)
        self.status = status


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_psutil(monkeypatch):
    """Replaces all psutil and platform calls with stubs returning fixed values.

    This fixture is defined in conftest.py, so pytest makes it available to
    every test file in this directory automatically — no import needed. Any
    test function (or fixture) that lists ``mock_psutil`` as a parameter
    will receive this fixture.

    ``monkeypatch`` is a built-in pytest fixture that lets you temporarily
    replace attributes, dictionary items, or environment variables for the
    duration of a single test.  Here it swaps real psutil and platform
    functions with simple fakes that return predictable values.

    Args:
        monkeypatch (pytest.MonkeyPatch): Built-in pytest fixture used to
            temporarily replace functions and attributes during a test.
    """

    def fake_cpu_count(logical=False):
        """Returns a fixed logical CPU count of 4.

        Args:
            logical (bool): Whether to count logical CPUs.

        Returns:
            int: Fixed CPU count.
        """
        return 4

    def fake_cpu_percent(interval=None):
        """Returns a fixed CPU usage percentage of 12.5.

        Args:
            interval (float | None): Time interval for measurement.

        Returns:
            float: Fixed CPU usage percentage.
        """
        return 12.5

    def fake_virtual_memory():
        """Returns a FakeVirtualMemory stub.

        Returns:
            FakeVirtualMemory: Stub with fixed memory values.
        """
        return FakeVirtualMemory()

    def fake_disk_partitions():
        """Returns a list containing a single FakeDiskPartition stub.

        Returns:
            list[FakeDiskPartition]: Single-element list of disk partitions.
        """
        return [FakeDiskPartition()]

    def fake_disk_usage(mountpoint):
        """Returns a FakeDiskUsage stub for any mountpoint.

        Args:
            mountpoint (str): The mount point path (ignored).

        Returns:
            FakeDiskUsage: Stub with fixed disk usage values.
        """
        return FakeDiskUsage()

    def fake_net_if_addrs():
        """Returns a dict with a single stubbed network interface.

        Returns:
            dict[str, list[FakeAddress]]: Mapping of interface name to addresses.
        """
        return {"eth0": [FakeAddress()]}

    def fake_net_io_counters(pernic=True):
        """Returns a dict with stubbed per-NIC IO counters.

        Args:
            pernic (bool): Whether to return per-NIC counters.

        Returns:
            dict[str, FakeIOCounters]: Mapping of interface name to IO counters.
        """
        return {"eth0": FakeIOCounters(1000, 2000)}

    def fake_process_iter(attrs=None):
        """Returns a list of stubbed process info objects.

        Args:
            attrs (list[str] | None): Process attributes to include.

        Returns:
            list[FakeProcessInfo]: List of fake process entries.
        """
        return [
            FakeProcessInfo("nginx", 1234),
            FakeProcessInfo("nginx", 1235),
            FakeProcessInfo("postgres", 5678),
        ]

    def fake_net_connections(kind="inet"):
        """Returns a list of stubbed network connections.

        Args:
            kind (str): Connection kind filter.

        Returns:
            list[FakeConnection]: List of fake connection entries.
        """
        return [
            FakeConnection("0.0.0.0", 80, "LISTEN"),
            FakeConnection("127.0.0.1", 5432, "LISTEN"),
        ]

    monkeypatch.setattr("psutil.cpu_count", fake_cpu_count)
    monkeypatch.setattr("psutil.cpu_percent", fake_cpu_percent)
    monkeypatch.setattr("psutil.virtual_memory", fake_virtual_memory)
    monkeypatch.setattr("psutil.disk_partitions", fake_disk_partitions)
    monkeypatch.setattr("psutil.disk_usage", fake_disk_usage)
    monkeypatch.setattr("psutil.net_if_addrs", fake_net_if_addrs)
    monkeypatch.setattr("psutil.net_io_counters", fake_net_io_counters)
    monkeypatch.setattr("psutil.process_iter", fake_process_iter)
    monkeypatch.setattr("psutil.net_connections", fake_net_connections)

    # NOTE FOR STUDENTS: The lines below use named functions instead of
    # commonly used lambda expressions.
    #
    # A lambda is just a shorthand for a small one-expression function.
    # For example:
    #     lambda: "Linux"
    # is equivalent to:
    #     def fake_platform_system():
    #         return "Linux"
    def fake_platform_system():
        return "Linux"

    def fake_platform_release():
        return "5.15.0"

    monkeypatch.setattr("platform.system", fake_platform_system)
    monkeypatch.setattr("platform.release", fake_platform_release)
