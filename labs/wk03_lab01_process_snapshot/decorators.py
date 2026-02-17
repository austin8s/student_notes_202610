"""
SOLUTION: Decorator implementations for the process monitor.
"""

import getpass
from datetime import datetime
from functools import wraps
from typing import Final

import psutil

DEFAULT_SUPPRESS: Final[tuple] = (
    PermissionError,
    psutil.AccessDenied,
    psutil.NoSuchProcess,
)


def suppress_errors(*exception_types):
    """
    EXAMPLE DECORATOR - Provided implementation.

    Decorator factory that suppresses specified exception types.

    Args:
        *exception_types: Variable length argument list of exception classes to suppress.
            If not provided, defaults to DEFAULT_SUPPRESS.

    Returns:
        function: Decorated function that suppresses specified exceptions.
    """
    if not exception_types:
        exception_types = DEFAULT_SUPPRESS

    def suppress_errors_decorator(func):
        """
        Inner decorator function.

        Args:
            func: The function to be decorated.

        Returns:
            function: Wrapped function with error suppression.
        """

        @wraps(func)
        def suppress_errors_wrapper(*args, **kwargs):
            """
            Wrapper function that handles exception suppression.

            Args:
                *args: Variable length argument list for wrapped function.
                **kwargs: Arbitrary keyword arguments for wrapped function.

            Returns:
                list: Result from wrapped function or empty list if error occurs.
            """
            try:
                return func(*args, **kwargs)
            except exception_types as e:
                print(f"[Suppressed Error] {type(e).__name__}: {e}")
                return []  # Return empty list for process functions

        return suppress_errors_wrapper

    return suppress_errors_decorator


def log_processes(filename="processes_snapshot.log"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Execute the decorated function
            processes = func(*args, **kwargs)
            
            try:
                # 2. Open file in write mode
                with open(filename, "w", encoding="utf-8") as f:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"{timestamp} - {len(processes)} processes\n")
                    f.write("=" * 120 + "\n")
                    
                    # Header
                    header = (
                        f"{'PID':<6} {'Name':<25} {'User':<15} {'CPU%':<6} "
                        f"{'Mem%':<6} {'Phys Mem(MB)':<14} {'Exe':<30} {'Cmdline'}\n"
                    )
                    f.write(header)
                    f.write("-" * 120 + "\n")
                    
                    # Process Rows
                    for proc in processes:
                        pid = str(proc.get('pid', ''))
                        name = str(proc.get('name', ''))
                        user = str(proc.get('username', ''))
                        cpu = f"{proc.get('cpu_percent', 0):.2f}"
                        mem = f"{proc.get('memory_percent', 0):.2f}"
                        
                        phys_bytes = proc.get('phys_mem', 0)
                        phys_mb = f"{(phys_bytes / (1024**2)):.2f}"
                        
                        exe = str(proc.get('exe', '')) or "-"
                        
                        cmd_list = proc.get('cmdline')
                        cmd = " ".join(cmd_list) if cmd_list else ""
                        
                        line = (
                            f"{pid:<6} {name:<25} {user:<15} {cpu:<6} "
                            f"{mem:<6} {phys_mb:<14} {exe:<30} {cmd}\n"
                        )
                        f.write(line)
                        
                print(f"[!] Process information logged to {filename}")
                
            except IOError as e:
                print(f"[Error] Could not write to log file: {e}")
            
            # 3. Return original process list
            return processes
        return wrapper
    return decorator


def filter_by_current_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        processes = func(*args, **kwargs)
        current_user = getpass.getuser()
        original_count = len(processes)
        
        print(f"[Filtering] getting only processes for user: {current_user}")
        
        filtered_processes = []
        for proc in processes:
            proc_user = proc.get('username')
            if proc_user and current_user in proc_user:
                filtered_processes.append(proc)
                
        print(f"[Filtering] Filtered from {original_count} to {len(filtered_processes)} processes")
        return filtered_processes
        
    return wrapper


def sort_processes(field="cpu_percent", reverse=True):
    """
    Decorator factory that allows sorting of process data by a specified field.

    Args:
        field (str, optional): The field to sort by. Defaults to "cpu_percent".
            Common fields: 'cpu_percent', 'memory_percent', 'pid', 'name'
        reverse (bool, optional): Sort in descending order. Defaults to True.

    Returns:
        function: Decorated function that sorts process list by specified field.
    """

    def sort_processes_decorator(func):
        """
        Inner decorator function.

        Args:
            func: The function to be decorated.

        Returns:
            function: Wrapped function with sorting capability.
        """

        @wraps(func)
        def sort_processes_wrapper(*args, **kwargs):
            """
            Wrapper function that sorts processes by specified field.

            Args:
                *args: Variable length argument list for wrapped function.
                **kwargs: Arbitrary keyword arguments for wrapped function.

            Returns:
                list: Sorted process list.
            """
            # Get the process list
            processes = func(*args, **kwargs)

            # Define sort key function
            def item_getter(proc):
                """
                Helper function to retrieve the sort key from a process dictionary.

                Args:
                    proc (dict): Dictionary containing process information.

                Returns:
                    Any: The value to be used for sorting (e.g., int, float, str).
                """
                # field is defined in the enclosing sort_process decorator
                # factory as a parameter
                sort_field = proc.get(field, 0)

                # Deal with process data like cmdlist that is a list
                # simply treat as a string and concatenate together all elements
                if type(sort_field) is list:
                    sort_field = " ".join(sort_field)

                return sort_field

            # Sort by specified field
            try:
                processes.sort(key=item_getter, reverse=reverse)
                print(
                    f"[Sorting] Sorted {len(processes)} processes by '{field}' "
                    f"({'descending' if reverse else 'ascending'})"
                )
            except TypeError as e:
                print(f"[Sorting Error] Could not sort by '{field}': {e}")

            return processes

        return sort_processes_wrapper

    return sort_processes_decorator


def max_listing(max_count=10):
    """
    Decorator factory that limits the number of processes returned.

    Args:
        max_count (int, optional): Maximum number of processes to return.
            Defaults to 10.

    Returns:
        function: Decorated function that limits process list to max_count.
    """

    def max_listing_decorator(func):
        """
        Inner decorator function.

        Args:
            func: The function to be decorated.

        Returns:
            function: Wrapped function with result limiting capability.
        """

        @wraps(func)
        def max_listing_wrapper(*args, **kwargs):
            """
            Wrapper function that limits the number of processes returned.

            Args:
                *args: Variable length argument list for wrapped function.
                **kwargs: Arbitrary keyword arguments for wrapped function.

            Returns:
                list: Limited process list with at most max_count items.
            """
            # Get the process list
            processes = func(*args, **kwargs)

            # Get the original count
            original_count = len(processes)

            # Limit to max_count
            limited_processes = processes[:max_count]

            # Print information about limiting
            if original_count > max_count:
                print(
                    f"[Max Listing] Limited from {original_count} to "
                    f"{len(limited_processes)} processes"
                )
            else:
                print(
                    f"[Max Listing] Returning all {original_count} processes "
                    f"(under limit of {max_count})"
                )

            return limited_processes

        return max_listing_wrapper

    return max_listing_decorator
