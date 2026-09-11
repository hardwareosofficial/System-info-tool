"""
linux_info.py — deep hardware detail on Linux.

Uses only things that ship on virtually every distro (/proc, /sys) plus
common CLI tools (lspci, lsblk, lsmod, dmidecode) when present. Every
function degrades gracefully — missing tools/permissions produce a note
instead of a crash, since some of this needs root (dmidecode, smartctl).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from typing import Any


def _run(cmd: list[str]) -> str | None:
    """Run a command if it exists on PATH; return stdout or None."""
    if shutil.which(cmd[0]) is None:
        return None
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        return out.stdout.strip()
    except Exception:
        return None


def _read(path: str) -> str | None:
    try:
        with open(path) as f:
            return f.read().strip()
    except (FileNotFoundError, PermissionError):
        return None


def get_cpu_detail() -> list[dict[str, Any]]:
    """Enhanced CPU information for Linux."""
    cpus = []
    info: dict[str, Any] = {}
    raw = _read("/proc/cpuinfo") or ""
    
    if not raw:
        return [{"Error": "Could not read /proc/cpuinfo"}]
    
    # Basic CPU info
    m = re.search(r"model name\s*:\s*(.+)", raw)
    if m:
        info["Name"] = m.group(1).strip()
        info["Model Name"] = m.group(1).strip()
    
    m = re.search(r"vendor_id\s*:\s*(.+)", raw)
    if m:
        info["Vendor"] = m.group(1).strip()
        info["Manufacturer"] = m.group(1).strip()
    
    m = re.search(r"cache size\s*:\s*(.+)", raw)
    if m:
        info["Cache Size"] = m.group(1).strip()
    
    # Architecture info
    m = re.search(r"cpu family\s*:\s*(.+)", raw)
    if m:
        info["CPU Family"] = m.group(1).strip()
    
    m = re.search(r"model\s*:\s*(.+)", raw)
    if m:
        info["Model"] = m.group(1).strip()
    
    m = re.search(r"stepping\s*:\s*(.+)", raw)
    if m:
        info["Stepping"] = m.group(1).strip()
    
    # Address size
    m = re.search(r"address sizes\s*:\s*(.+)", raw)
    if m:
        info["Address Sizes"] = m.group(1).strip()
        if "64" in m.group(1):
            info["CPU Mode"] = "64-bit"
        else:
            info["CPU Mode"] = "32-bit"
    
    flags = re.search(r"flags\s*:\s*(.+)", raw)
    if flags:
        important = {"avx", "avx2", "avx512f", "sse4_2", "aes", "virt", "vmx", "svm"}
        found = [f for f in flags.group(1).split() if f in important]
        info["Notable Flags"] = ", ".join(sorted(set(found))) or "n/a"

    # Governor / scaling driver, if exposed
    gov = _read("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
    if gov:
        info["Scaling Governor"] = gov
    driver = _read("/sys/devices/system/cpu/cpu0/cpufreq/scaling_driver")
    if driver:
        info["Scaling Driver"] = driver

    # Thermal zones
    temps = []
    base = "/sys/class/thermal"
    if os.path.isdir(base):
        for zone in sorted(os.listdir(base)):
            if not zone.startswith("thermal_zone"):
                continue
            t = _read(f"{base}/{zone}/temp")
            ty = _read(f"{base}/{zone}/type")
            if t:
                try:
                    temps.append(f"{ty or zone}: {int(t) / 1000:.1f}°C")
                except ValueError:
                    pass
    if temps:
        info["Thermal Zones"] = temps
    
    # Add core count from common module would be handled separately
    info["Status"] = "Active"
    
    cpus.append(info)
    return cpus


def get_gpu_detail() -> list[dict[str, Any]]:
    """Enhanced GPU information for Linux."""
    gpus = []
    gpu_index = 0
    lspci_present = shutil.which("lspci") is not None
    out = _run(["lspci", "-mm"])
    if out:
        for line in out.splitlines():
            if re.search(r"VGA compatible controller|3D controller|Display controller", line, re.I):
                gpu_index += 1
                parts = re.findall(r'"([^"]*)"', line)
                if len(parts) >= 3:
                    gpu_info = {
                        "GPU #": gpu_index,
                        "Name": parts[2],
                        "Manufacturer": parts[1],
                        "Class": parts[0],
                        "GPU Type": "Discrete" if "NVIDIA" in parts[1] or "AMD" in parts[1] else "Integrated",
                    }
                    gpus.append(gpu_info)
    if not gpus:
        # fallback: raw lspci grep (handles odd/short -mm output)
        raw = _run(["lspci"])
        if raw:
            for line in raw.splitlines():
                if re.search(r"VGA|3D controller", line, re.I):
                    gpu_index += 1
                    gpus.append({
                        "GPU #": gpu_index,
                        "Name": line,
                        "GPU Type": "Unknown"
                    })
    if not gpus:
        if not lspci_present:
            gpus.append({"Note": "lspci not available — install pciutils for GPU detail"})
        else:
            gpus.append({"Note": "No dedicated/display GPU found via PCI bus (headless system or virtual display)"})

    # Try NVIDIA-specific driver/VRAM info if nvidia-smi exists
    nv = _run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version,temperature.gpu",
               "--format=csv,noheader"])
    if nv:
        for i, line in enumerate(nv.splitlines()):
            fields = [x.strip() for x in line.split(",")]
            if len(fields) == 4 and i < len(gpus):
                gpus[i].update({
                    "Driver Version": fields[2],
                    "VRAM": fields[1],
                    "Temperature": fields[3],
                })
    return gpus


def get_motherboard_detail() -> dict[str, str]:
    """DMI info via /sys/class/dmi/id (root usually required for some fields)."""
    dmi_base = "/sys/class/dmi/id"
    fields = {
        "Board Vendor": "board_vendor",
        "Board Name": "board_name",
        "Board Version": "board_version",
        "Board Serial": "board_serial",
        "System Vendor": "sys_vendor",
        "Product Name": "product_name",
        "BIOS Vendor": "bios_vendor",
        "BIOS Version": "bios_version",
        "BIOS Release Date": "bios_date",
        "Chassis Type": "chassis_type",
    }
    result = {}
    for label, fname in fields.items():
        val = _read(f"{dmi_base}/{fname}")
        result[label] = val if val else "n/a (needs root or not exposed by firmware)"
    return result


def get_chipset_hint() -> dict[str, str]:
    """No universal 'chipset name' API on Linux; best-effort via lspci ISA/host bridge entry."""
    out = _run(["lspci"])
    if not out:
        return {"Chipset": "lspci not available — install pciutils"}
    for line in out.splitlines():
        if re.search(r"Host bridge|ISA bridge|LPC Controller", line, re.I):
            return {"Chipset (from PCI host/ISA bridge)": line.split(": ", 1)[-1]}
    return {"Chipset": "Not identifiable without dmidecode/root"}


def get_storage_detail() -> list[dict[str, Any]]:
    disks = []
    out = _run(["lsblk", "-d", "-o", "NAME,MODEL,SIZE,ROTA,TYPE,SERIAL", "-J"])
    if out:
        import json
        try:
            data = json.loads(out)
            for dev in data.get("blockdevices", []):
                disks.append({
                    "Device": f"/dev/{dev.get('name')}",
                    "Model": dev.get("model") or "n/a",
                    "Size": dev.get("size"),
                    "Type": "HDD (rotational)" if dev.get("rota") == "1" else "SSD/Flash",
                    "Kind": dev.get("type"),
                    "Serial": dev.get("serial") or "n/a (needs root)",
                })
        except Exception:
            pass
    if not disks:
        # fallback to /sys/block
        for name in sorted(os.listdir("/sys/block")):
            if name.startswith(("loop", "ram")):
                continue
            model = _read(f"/sys/block/{name}/device/model") or "n/a"
            disks.append({"Device": f"/dev/{name}", "Model": model})

    # SMART health, best-effort, needs smartmontools + usually root
    if shutil.which("smartctl"):
        for d in disks:
            health = _run(["smartctl", "-H", d["Device"]])
            if health:
                m = re.search(r"(PASSED|FAILED|OK)", health, re.I)
                d["SMART Health"] = m.group(1) if m else "unknown"
            else:
                d["SMART Health"] = "n/a (needs root, or unsupported)"
    else:
        for d in disks:
            d["SMART Health"] = "smartmontools not installed"
    return disks


def get_drivers_detail(limit: int = 60) -> list[dict[str, str]]:
    """Loaded kernel modules == the closest Linux equivalent to 'drivers'.

    Prefers `lsmod` (nicer formatting) but falls back to /proc/modules,
    which is always present on Linux regardless of PATH/util availability.
    """
    modules = []
    out = _run(["lsmod"])
    if out:
        lines = out.splitlines()[1:]  # skip header
        for line in lines[:limit]:
            fields = line.split()
            if len(fields) >= 3:
                modules.append({
                    "Module": fields[0],
                    "Size": fields[1],
                    "Used By": fields[2],
                })

    if not modules:
        raw = _read("/proc/modules")
        if raw:
            for line in raw.splitlines()[:limit]:
                fields = line.split()
                if len(fields) >= 3:
                    modules.append({
                        "Module": fields[0],
                        "Size": fields[1],
                        "Used By Count": fields[2],
                    })

    if not modules:
        modules.append({"Note": "No loadable kernel modules found (or /proc not mounted)"})
    return modules


def get_battery_detailed_info() -> dict[str, Any]:
    """Get battery information from /sys/class/power_supply (Linux)."""
    base = "/sys/class/power_supply"
    result: dict[str, Any] = {}
    try:
        if not os.path.isdir(base):
            return {"Note": "No power_supply sysfs present"}

        bats = [d for d in os.listdir(base) if d.lower().startswith("bat") or d.lower().startswith("battery")]
        if not bats:
            # try filtering for devices with type "Battery"
            for d in os.listdir(base):
                t = _read(f"{base}/{d}/type")
                if t and t.lower() == "battery":
                    bats.append(d)
        if not bats:
            return {"Note": "No battery devices found"}

        # Use first battery
        bat = bats[0]
        fields = {
            "Status": "status",
            "Charge Now": "charge_now",
            "Charge Full": "charge_full",
            "Energy Now": "energy_now",
            "Energy Full": "energy_full",
            "Power Now": "power_now",
            "Current Now": "current_now",
            "Voltage Now": "voltage_now",
            "Manufacturer": "manufacturer",
            "Model Name": "model_name",
            "Serial Number": "serial_number",
        }

        for label, fname in fields.items():
            val = _read(f"{base}/{bat}/{fname}")
            if val:
                result[label] = val

        # Compute percentage if possible
        try:
            if "Charge Now" in result and "Charge Full" in result:
                cn = int(result["Charge Now"])
                cf = int(result["Charge Full"])
                if cf > 0:
                    result["Estimated Charge Remaining (%)"] = round((cn / cf) * 100, 1)
        except Exception:
            pass

        # Estimated time and power using energy_now/power_now or charge/current
        try:
            if "Power Now" in result and result["Power Now"]:
                # units are microWatts (uW) for power_now; energy in uWh
                power_uw = int(result["Power Now"])
                power_w = power_uw / 1_000_000.0
                result["Power (W)"] = f"{power_w:.3f} W"
                if "Energy Now" in result and result["Energy Now"]:
                    energy_uwh = int(result["Energy Now"])
                    hours = energy_uwh / power_uw if power_uw > 0 else None
                    if hours is not None:
                        mins = int(hours * 60)
                        result["Estimated Run Time (min)"] = mins
            elif "Current Now" in result and "Voltage Now" in result:
                # current in uA, voltage in uV maybe — best-effort
                try:
                    cur_ua = int(result.get("Current Now", 0))
                    volt_uv = int(result.get("Voltage Now", 0))
                    power_w = (cur_ua * volt_uv) / 1_000_000_000.0
                    result["Power (W)"] = f"{power_w:.3f} W (approx)"
                except Exception:
                    pass
        except Exception:
            pass

        return result
    except Exception:
        return {"Error": "Could not read battery information from sysfs"}


def get_network_hardware() -> list[dict[str, str]]:
    out = _run(["lspci"])
    nics = []
    if out:
        for line in out.splitlines():
            if re.search(r"Ethernet controller|Network controller|Wireless", line, re.I):
                nics.append({"Device": line.split(": ", 1)[-1]})
    return nics
