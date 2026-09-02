"""
macos_info.py — deep hardware detail on macOS.

Uses system_profiler and other macOS-specific commands to gather hardware information.
All functions degrade gracefully if commands are not available or fail.
"""
from __future__ import annotations

import subprocess
import re
from typing import Any


def _run(cmd: list[str]) -> str | None:
    """Run a command and return stdout or None if it fails."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None


def get_cpu_detail() -> list[dict[str, Any]]:
    """Get CPU information using system_profiler."""
    cpus = []
    try:
        out = _run(["system_profiler", "SPHardwareDataType"])
        if out:
            # Extract CPU info
            cpu_match = re.search(r"Chip:\s*(.+)", out)
            if cpu_match:
                cpu_name = cpu_match.group(1).strip()
                cpus.append({
                    "Name": cpu_name,
                    "Architecture": "ARM64" if "Apple" in cpu_name else "x86_64",
                    "CPU Mode": "64-bit",
                    "Status": "Active",
                })
            
            # Additional CPU details
            cores_match = re.search(r"Number of (Cores|Processors):\s*(\d+)", out)
            if cores_match:
                if cpus:
                    cpus[0]["Cores"] = int(cores_match.group(2))
    except Exception:
        pass
    
    if not cpus:
        cpus.append({"Note": "Could not retrieve CPU information via system_profiler"})
    
    return cpus


def get_gpu_detail() -> list[dict[str, Any]]:
    """Get GPU information using system_profiler."""
    gpus = []
    try:
        out = _run(["system_profiler", "SPDisplaysDataType"])
        if out:
            # Parse GPU information
            gpu_blocks = re.split(r"\n\s*\n", out)
            for block in gpu_blocks:
                if "Chipset Model" in block or "GPU" in block:
                    gpu_info = {}
                    name_match = re.search(r"Chipset Model:\s*(.+)", block)
                    if name_match:
                        gpu_info["Name"] = name_match.group(1).strip()
                    
                    vram_match = re.search(r"VRAM:\s*(.+)", block)
                    if vram_match:
                        gpu_info["VRAM"] = vram_match.group(1).strip()
                    
                    vendor_match = re.search(r"Vendor:\s*(.+)", block)
                    if vendor_match:
                        gpu_info["Manufacturer"] = vendor_match.group(1).strip()
                    
                    gpu_type = "Integrated" if "Apple" in gpu_info.get("Name", "") else "Discrete"
                    gpu_info["GPU Type"] = gpu_type
                    
                    if gpu_info:
                        gpus.append(gpu_info)
    except Exception:
        pass
    
    if not gpus:
        gpus.append({"Note": "Could not retrieve GPU information via system_profiler"})
    
    return gpus


def get_motherboard_detail() -> dict[str, Any]:
    """Get motherboard/system information using system_profiler."""
    result = {}
    try:
        out = _run(["system_profiler", "SPHardwareDataType"])
        if out:
            model_match = re.search(r"Model Name:\s*(.+)", out)
            if model_match:
                result["System Model"] = model_match.group(1).strip()
            
            model_id_match = re.search(r"Model Identifier:\s*(.+)", out)
            if model_id_match:
                result["Model Identifier"] = model_id_match.group(1).strip()
            
            serial_match = re.search(r"Serial Number:\s*(.+)", out)
            if serial_match:
                result["Serial Number"] = serial_match.group(1).strip()
            
            uuid_match = re.search(r"Hardware UUID:\s*(.+)", out)
            if uuid_match:
                result["Hardware UUID"] = uuid_match.group(1).strip()
            
            boot_rom_match = re.search(r"Boot ROM Version:\s*(.+)", out)
            if boot_rom_match:
                result["Boot ROM Version"] = boot_rom_match.group(1).strip()
            
            smc_match = re.search(r"SMC Version.*?:\s*(.+)", out)
            if smc_match:
                result["SMC Version"] = smc_match.group(1).strip()
    except Exception:
        pass
    
    if not result:
        result = {"Note": "Could not retrieve motherboard information via system_profiler"}
    
    return result


def get_chipset_hint() -> dict[str, Any]:
    """Get chipset information (limited on macOS)."""
    try:
        out = _run(["system_profiler", "SPHardwareDataType"])
        if out:
            chip_match = re.search(r"Chip:\s*(.+)", out)
            if chip_match:
                return {"Chipset": chip_match.group(1).strip()}
    except Exception:
        pass
    
    return {"Chipset": "Not directly available on macOS (integrated with SoC)"}


def get_storage_detail() -> list[dict[str, Any]]:
    """Get storage information using system_profiler and diskutil."""
    disks = []
    try:
        # Get physical storage info
        out = _run(["system_profiler", "SPStorageDataType"])
        if out:
            # Parse storage information
            storage_blocks = re.split(r"\n\s*\n", out)
            for block in storage_blocks:
                if "Capacity:" in block or "Medium:" in block:
                    disk_info = {}
                    
                    capacity_match = re.search(r"Capacity:\s*(.+)", block)
                    if capacity_match:
                        disk_info["Size"] = capacity_match.group(1).strip()
                    
                    model_match = re.search(r"Model:\s*(.+)", block)
                    if model_match:
                        disk_info["Model"] = model_match.group(1).strip()
                    
                    medium_match = re.search(r"Medium Type:\s*(.+)", block)
                    if medium_match:
                        disk_info["Media Type"] = medium_match.group(1).strip()
                    
                    # Determine storage type
                    model = disk_info.get("Model", "").lower()
                    if "ssd" in model or "flash" in model:
                        disk_info["Storage Type"] = "SSD"
                    elif "hdd" in model or "hard" in model:
                        disk_info["Storage Type"] = "HDD"
                    else:
                        disk_info["Storage Type"] = "Unknown"
                    
                    if disk_info:
                        disks.append(disk_info)
    except Exception:
        pass
    
    if not disks:
        # Fallback to diskutil
        try:
            out = _run(["diskutil", "list"])
            if out:
                disk_matches = re.findall(r"/dev/disk\d+", out)
                for disk in disk_matches:
                    disks.append({"Device": disk, "Model": "n/a (use diskutil info for details)"})
        except Exception:
            pass
    
    if not disks:
        disks.append({"Note": "Could not retrieve storage information"})
    
    return disks


def get_drivers_detail(limit: int = 50) -> list[dict[str, Any]]:
    """Get kernel extensions (kexts) information - macOS equivalent of drivers."""
    drivers = []
    try:
        out = _run(["kextstat", "-l"])
        if out:
            lines = out.splitlines()[:limit]
            for line in lines:
                # Parse kextstat output
                fields = line.split()
                if len(fields) >= 5:
                    drivers.append({
                        "Extension": fields[4],
                        "Version": fields[1] if len(fields) > 1 else "n/a",
                        "Index": fields[0] if len(fields) > 0 else "n/a",
                    })
    except Exception:
        pass
    
    if not drivers:
        drivers.append({"Note": "Could not retrieve kernel extension information"})
    
    return drivers


def get_network_hardware() -> list[dict[str, Any]]:
    """Get network hardware information using system_profiler."""
    network_info = []
    try:
        out = _run(["system_profiler", "SPNetworkDataType"])
        if out:
            # Parse network interfaces
            interface_blocks = re.split(r"\n\s*\n", out)
            for block in interface_blocks:
                if "Type:" in block or "Hardware:" in block:
                    iface = {}
                    
                    type_match = re.search(r"Type:\s*(.+)", block)
                    if type_match:
                        iface["Type"] = type_match.group(1).strip()
                    
                    hardware_match = re.search(r"Hardware:\s*(.+)", block)
                    if hardware_match:
                        iface["Hardware"] = hardware_match.group(1).strip()
                    
                    if iface:
                        network_info.append(iface)
    except Exception:
        pass
    
    if not network_info:
        network_info.append({"Note": "Could not retrieve network hardware information"})
    
    return network_info


def get_bios_detailed_info() -> dict[str, Any]:
    """Get firmware information (equivalent to BIOS on macOS)."""
    result = {}
    try:
        out = _run(["system_profiler", "SPHardwareDataType"])
        if out:
            boot_rom_match = re.search(r"Boot ROM Version:\s*(.+)", out)
            if boot_rom_match:
                result["Firmware Version"] = boot_rom_match.group(1).strip()
            
            smc_match = re.search(r"SMC Version.*?:\s*(.+)", out)
            if smc_match:
                result["SMC Version"] = smc_match.group(1).strip()
            
            result["BIOS Type"] = "EFI (Apple)"  # Macs use EFI, not traditional BIOS
    except Exception:
        pass
    
    if not result:
        result = {"Note": "Could not retrieve firmware information"}
    
    return result


def get_battery_detailed_info() -> dict[str, Any]:
    """Get detailed battery information using system_profiler."""
    result = {}
    try:
        out = _run(["system_profiler", "SPPowerDataType"])
        if out:
            # Parse battery information
            charge_match = re.search(r"Charge Information:\s*\n\s*Remaining:\s*(.+)", out)
            if charge_match:
                result["Charge Remaining"] = charge_match.group(1).strip()
            
            full_charge_match = re.search(r"Full Charge:\s*(.+)", out)
            if full_charge_match:
                result["Full Charge Capacity"] = full_charge_match.group(1).strip()
            
            health_match = re.search(r"Condition:\s*(.+)", out)
            if health_match:
                result["Health"] = health_match.group(1).strip()
            
            cycle_count_match = re.search(r"Cycle Count:\s*(\d+)", out)
            if cycle_count_match:
                result["Cycle Count"] = int(cycle_count_match.group(1))
    except Exception:
        pass
    
    if not result:
        result = {"Note": "Could not retrieve battery information"}
    
    return result


def get_smbios_detailed_info() -> dict[str, Any]:
    """Get SMBIOS-like information using system_profiler."""
    result = {}
    try:
        out = _run(["system_profiler", "SPHardwareDataType"])
        if out:
            model_match = re.search(r"Model Name:\s*(.+)", out)
            if model_match:
                result["System Model"] = model_match.group(1).strip()
            
            model_id_match = re.search(r"Model Identifier:\s*(.+)", out)
            if model_id_match:
                result["Model Identifier"] = model_id_match.group(1).strip()
            
            serial_match = re.search(r"Serial Number:\s*(.+)", out)
            if serial_match:
                result["Serial Number"] = serial_match.group(1).strip()
            
            uuid_match = re.search(r"Hardware UUID:\s*(.+)", out)
            if uuid_match:
                result["Hardware UUID"] = uuid_match.group(1).strip()
    except Exception:
        pass
    
    if not result:
        result = {"Note": "Could not retrieve SMBIOS-like information"}
    
    return result