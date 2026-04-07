"""Dataclass models for system monitoring metrics."""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class MemoryMetrics:
    """Represents memory usage statistics.

    Attributes:
        total (int): Total memory in bytes.
        used (int): Used memory in bytes.
        percent (float): Percentage of memory used.
    """

    total: int
    used: int
    percent: float

    def __str__(self) -> str:
        """Returns a human-readable string representation.

        Returns:
            str: Formatted string of memory metrics.
        """
        return (
            f"MemoryMetrics(total={self.total}, "
            f"used={self.used}, "
            f"percent={self.percent})"
        )

    def to_dict(self):
        """Converts the report to a dictionary.

        Returns:
            dict: Dictionary representation of the report.
        """
        return asdict(self)


@dataclass(frozen=True)
class DiskMetrics:
    """Represents disk partition usage statistics.

    Attributes:
        device (str): Device name.
        mountpoint (str): Mount point path.
        fstype (str): Filesystem type.
        total (int): Total space in bytes.
        used (int): Used space in bytes.
        free (int): Free space in bytes.
        percent (float): Percentage of space used.
    """

    device: str
    mountpoint: str
    fstype: str
    total: int
    used: int
    free: int
    percent: float

    def __str__(self) -> str:
        """Returns a human-readable string representation.

        Returns:
            str: Formatted string of disk metrics.
        """
        return (
            f"DiskMetrics(device={self.device}, "
            f"mountpoint={self.mountpoint}, "
            f"fstype={self.fstype}, "
            f"total={self.total}, "
            f"used={self.used}, "
            f"free={self.free}, "
            f"percent={self.percent})"
        )

    def to_dict(self):
        """Converts the report to a dictionary.

        Returns:
            dict: Dictionary representation of the report.
        """
        return asdict(self)


@dataclass(frozen=True)
class NetworkDeviceMetrics:
    """Represents network device statistics.

    Attributes:
        name (str): Network device name.
        ips (list[str]): List of IP addresses.
        bytes_sent_since_last (int): Bytes sent since last report.
        bytes_recv_since_last (int): Bytes received since last report.
    """

    name: str
    ips: List[str]
    bytes_sent_since_last: int
    bytes_recv_since_last: int

    def __str__(self) -> str:
        """Returns a human-readable string representation.

        Returns:
            str: Formatted string of network device metrics.
        """
        return (
            f"NetworkDeviceMetrics(name={self.name}, ips={self.ips}, "
            f"bytes_sent_since_last={self.bytes_sent_since_last}, "
            f"bytes_recv_since_last={self.bytes_recv_since_last})"
        )

    def to_dict(self):
        """Converts the report to a dictionary.

        Returns:
            dict: Dictionary representation of the report.
        """
        return asdict(self)


@dataclass(frozen=True)
class MonitorMetrics:
    """Represents a full system monitoring report.

    Attributes:
        timestamp (datetime): Timestamp when the report was generated.
        os_type (str): Operating system type (e.g., 'Windows', 'Linux').
        os_version (str): Operating system release version.
        cpu_count (int): Number of logical CPUs.
        cpu_percent (float): System-wide CPU usage percentage
            since last report (not per-core).
        memory (MemoryMetrics): Memory usage statistics.
        disks (list[DiskMetrics]): List of disk usage statistics.
        network (list[NetworkDeviceMetrics]): List of network device statistics.
    """

    timestamp: datetime
    os_type: str
    os_version: str
    cpu_count: int
    cpu_percent: float
    memory: MemoryMetrics
    disks: List[DiskMetrics]
    network: List[NetworkDeviceMetrics]

    def __str__(self) -> str:
        """Returns a human-readable string representation.

        Returns:
            str: Formatted multi-line string of all system metrics.
        """
        return (
            f"MonitorMetrics(\n"
            f"\ttimestamp={self.timestamp},\n"
            f"\tos_type={self.os_type},\n"
            f"\tos_version={self.os_version},\n"
            f"\tcpu_count={self.cpu_count},\n"
            f"\tcpu_percent={self.cpu_percent},\n"
            f"\tmemory={self.memory},\n"
            "\tdisks=[\n\t\t" + ",\n\t\t".join(str(d) for d in self.disks) + "\n\t],\n"
            "\tnetwork=[\n\t\t"
            + ",\n\t\t".join(str(n) for n in self.network)
            + "\n\t]\n)"
        )

    def to_dict(self):
        """Converts the report to a dictionary.

        Returns:
            dict: Dictionary representation of the report.
        """
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    def to_json(self) -> str:
        """Converts the report to a JSON-formatted string.

        Returns:
            str: JSON string of the report.
        """
        return json.dumps(self.to_dict(), indent=2)
