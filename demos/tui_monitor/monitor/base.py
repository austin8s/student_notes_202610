"""Base system monitor for collecting CPU, memory, disk, and network metrics."""

import platform
from datetime import datetime
from typing import List

import psutil

from .metric_models import (
    DiskMetrics,
    MemoryMetrics,
    MonitorMetrics,
    NetworkDeviceMetrics,
)


class Monitor:
    """System monitor for reporting CPU, memory, disk, and network statistics.

    Tracks deltas for CPU and network usage since the last report.
    """

    def __init__(self):
        """Initializes the Monitor with baseline snapshots for delta calculations."""
        self._last_cpu_times = psutil.cpu_times()
        self._last_net = psutil.net_io_counters(pernic=True)
        self._last_cpu_percent = psutil.cpu_percent(interval=None)

    @property
    def os_type(self) -> str:
        """Gets the operating system type.

        Returns:
            str: The OS type (e.g., 'Windows', 'Linux', 'Darwin').
        """
        return platform.system()

    @property
    def os_version(self) -> str:
        """Gets the operating system release version.

        Returns:
            str: The OS release version string.
        """
        return platform.release()

    @property
    def cpu_count(self) -> int:
        """Gets the number of logical CPUs in the system.

        Returns:
            int: Number of logical CPUs.
        """
        # Only show physical Cores and CPU's not logical (hyper-threading)
        cpu_count = psutil.cpu_count(logical=False)
        return cpu_count if cpu_count else 0

    @property
    def cpu_percent(self) -> float:
        """Gets the system-wide CPU usage percentage.

        Returns:
            float: System-wide CPU usage percentage (not per-core).
        """
        return psutil.cpu_percent(interval=0.1)

    @property
    def memory(self) -> MemoryMetrics:
        """Gets total and current memory usage statistics.

        Returns:
            MemoryMetrics: Dataclass with total, used, and percent memory usage.
        """
        mem = psutil.virtual_memory()
        return MemoryMetrics(total=mem.total, used=mem.used, percent=mem.percent)

    @property
    def disks(self) -> List[DiskMetrics]:
        """Gets a list of disk devices and mounted partitions with usage statistics.

        Returns:
            list[DiskMetrics]: List of DiskMetrics dataclasses.
        """
        disks = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks.append(
                    DiskMetrics(
                        device=part.device,
                        mountpoint=part.mountpoint,
                        fstype=part.fstype,
                        total=usage.total,
                        used=usage.used,
                        free=usage.free,
                        percent=usage.percent,
                    )
                )
            except (PermissionError, OSError):
                continue
        return disks

    @property
    def network(self) -> List[NetworkDeviceMetrics]:
        """Gets network devices with IP addresses and traffic since last report.

        Returns:
            list[NetworkDeviceMetrics]: List of NetworkDeviceMetrics dataclasses.
        """
        net_addrs = psutil.net_if_addrs()
        net_io = psutil.net_io_counters(pernic=True)
        devices = []
        for name, addrs in net_addrs.items():
            ips = [
                addr.address
                for addr in addrs
                if addr.family.name in ("AF_INET", "AF_INET6")
            ]
            io = net_io.get(name)
            last_io = self._last_net.get(name)
            if io and last_io:
                bytes_sent = io.bytes_sent - last_io.bytes_sent
                bytes_recv = io.bytes_recv - last_io.bytes_recv
            else:
                bytes_sent = io.bytes_sent if io else 0
                bytes_recv = io.bytes_recv if io else 0
            devices.append(
                NetworkDeviceMetrics(
                    name=name,
                    ips=ips,
                    bytes_sent_since_last=bytes_sent,
                    bytes_recv_since_last=bytes_recv,
                )
            )
        return devices

    @property
    def metrics(self) -> MonitorMetrics:
        """Generates a structured report of all system metrics with a timestamp.

        Returns:
            MonitorMetrics: Dataclass containing the system metrics and timestamp.
        """
        os_type = self.os_type
        os_version = self.os_version
        cpu_count = self.cpu_count
        cpu_percent = self.cpu_percent
        memory = self.memory
        disks = self.disks
        network = self.network
        timestamp = datetime.now()

        # Update last network snapshot
        self._last_net = psutil.net_io_counters(pernic=True)

        return MonitorMetrics(
            timestamp=timestamp,
            os_type=os_type,
            os_version=os_version,
            cpu_count=cpu_count,
            cpu_percent=cpu_percent,
            memory=memory,
            disks=disks,
            network=network,
        )
