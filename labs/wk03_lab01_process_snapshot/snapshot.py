"""
System process snapshot tool using psutil.
"""

import time
from typing import Final

import psutil
from decorators import (
    filter_by_current_user,
    log_processes,
    max_listing,
    sort_processes,
    suppress_errors,
)

LOG_FILE: Final[str] = "process_snapshot.log"

@log_processes(LOG_FILE)                   
@max_listing(15)                          
@sort_processes("phys_mem", reverse=True)  
@filter_by_current_user
@suppress_errors(
    psutil.ZombieProcess, PermissionError, psutil.AccessDenied, psutil.NoSuchProcess
)
def get_processes_info():
    """
    Get processes info

    Args:
        cpu_threshold: CPU percentage threshold per core
        memory_threshold: Memory percentage threshold

    Returns:
        list: List of process dictionaries
    """
    proccesses = []

    # get actual core count - ignore logical cores
    cpu_count = psutil.cpu_count(logical=False)

    # loop over all processes once to prime cpu utilization
    for process in psutil.process_iter():

        # Get process cpu_percent only reading necessary at this time
        process_info = process.cpu_percent()

    # Pause to give system time to gather readings on CPU%
    time.sleep(2)

    for process in psutil.process_iter():
        # Get process info using as_dict
        # Get CPU percent - have to perform twice to get usage between checks
        process_info = process.as_dict(
            attrs=[
                "pid",
                "name",
                "exe",
                "cmdline",
                "status",
                "username",
                "memory_info",
                "memory_percent",
                "cpu_percent",
            ]
        )

        # Convert CPU % to be for whole system not just one core
        process_info["cpu_percent"] = process_info["cpu_percent"] / cpu_count

        # get physcal memory usage and add it as an element
        # to process info so it can be accessed directly
        process_info["phys_mem"] = process_info["memory_info"].rss

        proccesses.append(process_info)

    return proccesses


def print_process_info(processes):
    """
    Print formatted information about processes.

    Args:
        processes: List of process dictionaries
    """
    BYTES_PER_MB = 1024**24

    if not processes:
        print("\nNo processes ")
        return

    print("\n" + "=" * 80)
    print("PROCESSES")
    print("=" * 80)

    for index, proc in enumerate(processes, 1):
        print(f"\n[Process {index}]")
        print(f"  Name:              {proc['name']}")
        print(f"  PID:               {proc['pid']}")
        print(f"  Executable:        {proc['exe'] or 'N/A'}")

        # Format cmdline (can be very long)
        cmdline = " ".join(proc["cmdline"]) if proc["cmdline"] else "N/A"
        if len(cmdline) > 80:
            cmdline = "..." + cmdline[-77:]
        print(f"  Command Line:      {cmdline}")
        print(f"  Username:         {proc['username'] or 'N/A'}")
        print(f"  CPU:             {proc['cpu_percent']:6.2f}% per core")
        print(f"  Memory:          {proc['memory_percent']:6.2f}%")
        print(f"  Physical Memory: {proc['phys_mem']/BYTES_PER_MB:6.2f} MB")


def main():
    """Main entry point."""
    print("=" * 60)
    print("System Resource Process Snapshot")
    print("=" * 60)
    print("\nScanning for processes...")
    print("(This will take a few seconds to measure CPU usage)")

    procs = get_processes_info()

    print_process_info(procs)
    print("\n" + "=" * 60)
    print(f"Total processes found: {len(procs)}")
    print("Process information logged to process_snapshot.log")


if __name__ == "__main__":
    main()
