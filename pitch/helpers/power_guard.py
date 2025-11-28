import platform
import ctypes
import subprocess
import os
import signal
from typing import Optional

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

# Track the caffeinate process globally
_caffeinate_process: Optional[subprocess.Popen] = None


def prevent_sleep():
    global _caffeinate_process

    system = platform.system()
    if system == "Windows":
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        )
    elif system == "Darwin":  # macOS
        if _caffeinate_process is None:
            _caffeinate_process = subprocess.Popen(["caffeinate", "-diu"])
    # Add more OSes as needed


def allow_sleep():
    global _caffeinate_process

    system = platform.system()
    if system == "Windows":
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    elif system == "Darwin":  # macOS
        if _caffeinate_process is not None:
            os.kill(_caffeinate_process.pid, signal.SIGTERM)
            _caffeinate_process = None
