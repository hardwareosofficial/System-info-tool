"""Threaded smoke test for the WMI collectors.

This script spawns a worker thread that calls `collectors.windows_info.get_cpu_detail()`
so we exercise COM initialization on a non-main thread.

Note: Requires Windows with `pywin32` and `wmi` installed for full results.
If those packages are missing, the collector will return an error dict instead
of raising an exception.
"""
from __future__ import annotations

import threading
import time
import sys
import os

# Ensure the repository root is on sys.path so `collectors` can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from collectors import windows_info


def worker():
    try:
        print("Worker: calling get_cpu_detail()")
        res = windows_info.get_cpu_detail()
        print("Worker: result type:", type(res))
        print(res)
    except Exception as e:
        print("Worker: exception:", e)


if __name__ == "__main__":
    t = threading.Thread(target=worker, name="WMIWorker")
    t.start()
    t.join(timeout=30)
    if t.is_alive():
        print("Worker thread did not finish within timeout", file=sys.stderr)
        sys.exit(2)
    print("Smoke test finished")
