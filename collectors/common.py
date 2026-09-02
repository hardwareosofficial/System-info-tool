"""
common.py — cross-platform data collection (Windows 8/8.1/10/11 + Linux)

Everything in here relies only on the Python standard library + psutil,
so it works the same on every supported OS. Platform-specific modules
(windows.py / linux.py) add the deeper hardware detail on top of this.
"""
from __future__ import annotations

import datetime
import platform
import socket
import getpass
import uuid
from typing import Any

import psutil


def _bytes_to_gb(n: int) -> float:
    return round(n / (1024 ** 3), 2)


def get_os_info() -> dict[str, Any]:
    uname = platform.uname()
    boot_ts = psutil.boot_time()
    boot_time = datetime.datetime.fromtimestamp(boot_ts)
    uptime = datetime.datetime.now() - boot_time

    info = {
        "Hostname": uname.node,
        "OS": uname.system,
        "OS Release": uname.release,
        "OS Version (build)": uname.version,
        "Architecture": uname.machine,
        "Python Runtime": platform.python_version(),
        "Current User": getpass.getuser(),
        "Boot Time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Uptime": str(uptime).split(".")[0],
        "Machine UUID (session)": str(uuid.getnode()),
    }

    if platform.system() == "Windows":
        info["Windows Edition"] = platform.win32_edition() if hasattr(platform, "win32_edition") else "n/a"
        try:
            info["Windows Version Tuple"] = str(platform.win32_ver())
        except Exception:
            pass
    elif platform.system() == "Linux":
        info.update(_linux_distro_info())

    return info


def _linux_distro_info() -> dict[str, str]:
    data = {}
    try:
        with open("/etc/os-release") as f:
            kv = {}
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    kv[k] = v.strip('"')
        data["Distro"] = kv.get("PRETTY_NAME", "Unknown Linux")
        data["Distro ID"] = kv.get("ID", "")
    except FileNotFoundError:
        data["Distro"] = "Unknown (no /etc/os-release)"
    try:
        with open("/proc/version") as f:
            data["Kernel Build String"] = f.read().strip()
    except FileNotFoundError:
        pass
    return data


def get_cpu_basic() -> dict[str, Any]:
    freq = psutil.cpu_freq()
    return {
        "Physical Cores": psutil.cpu_count(logical=False),
        "Logical Processors": psutil.cpu_count(logical=True),
        "Current Frequency (MHz)": round(freq.current, 1) if freq else "n/a",
        "Min Frequency (MHz)": round(freq.min, 1) if freq and freq.min else "n/a",
        "Max Frequency (MHz)": round(freq.max, 1) if freq and freq.max else "n/a",
        "Overall Usage (%)": psutil.cpu_percent(interval=0.3),
        "Per-Core Usage (%)": psutil.cpu_percent(interval=0.3, percpu=True),
    }


def get_memory_info() -> dict[str, Any]:
    vm = psutil.virtual_memory()
    sw = psutil.swap_memory()
    return {
        "Total RAM (GB)": _bytes_to_gb(vm.total),
        "Used RAM (GB)": _bytes_to_gb(vm.used),
        "Available RAM (GB)": _bytes_to_gb(vm.available),
        "RAM Usage (%)": vm.percent,
        "Total Swap/Page File (GB)": _bytes_to_gb(sw.total),
        "Used Swap/Page File (GB)": _bytes_to_gb(sw.used),
    }


def get_disk_info() -> list[dict[str, Any]]:
    disks = []
    for part in psutil.disk_partitions(all=False):
        entry = {
            "Device": part.device,
            "Mountpoint": part.mountpoint,
            "Filesystem": part.fstype,
        }
        try:
            usage = psutil.disk_usage(part.mountpoint)
            entry["Total (GB)"] = _bytes_to_gb(usage.total)
            entry["Used (GB)"] = _bytes_to_gb(usage.used)
            entry["Free (GB)"] = _bytes_to_gb(usage.free)
            entry["Used (%)"] = usage.percent
        except PermissionError:
            entry["Total (GB)"] = "n/a (permission denied)"
        disks.append(entry)
    return disks


def get_network_info() -> list[dict[str, Any]]:
    ifaces = []
    stats = psutil.net_if_stats()
    addrs = psutil.net_if_addrs()
    for name, addr_list in addrs.items():
        st = stats.get(name)
        entry = {
            "Interface": name,
            "Up": st.isup if st else "n/a",
            "Speed (Mbps)": st.speed if st else "n/a",
            "MTU": st.mtu if st else "n/a",
            "Addresses": [a.address for a in addr_list],
        }
        ifaces.append(entry)
    return ifaces


def get_battery_info() -> dict[str, Any] | None:
    try:
        batt = psutil.sensors_battery()
    except Exception:
        return None
    if batt is None:
        return None
    return {
        "Percent": batt.percent,
        "Plugged In": batt.power_plugged,
        "Time Left (min)": "n/a" if batt.secsleft in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN)
        else round(batt.secsleft / 60, 1),
    }


def get_processes_summary(top_n: int = 10) -> list[dict[str, Any]]:
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: x.get("memory_percent") or 0, reverse=True)
    return procs[:top_n]
