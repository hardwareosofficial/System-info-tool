"""
aggregate.py — single entry point the GUI (and the HTML report) calls.

Merges the cross-platform (`common.py`) data with whichever
platform-specific module applies, and always returns plain
dict/list-of-dict structures so both the GUI and the HTML renderer
can walk them generically without caring which OS produced them.
"""
from __future__ import annotations

import platform
from typing import Any

from . import common

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MACOS = platform.system() == "Darwin"

# Platform-specific imports are handled safely below
_plat = None

if IS_WINDOWS:
    try:
        from . import windows_info as _plat
    except ImportError:
        _plat = None
elif IS_LINUX:
    try:
        from . import linux_info as _plat
    except ImportError:
        _plat = None
elif IS_MACOS:
    try:
        from . import macos_info as _plat
    except ImportError:
        _plat = None
else:
    _plat = None  # Other platforms: cross-platform data only


def _safe(fn, *args, **kwargs):
    """Never let one failed probe (permissions, missing tool, missing WMI
    class on an old Windows build, etc.) take down the whole report."""
    if fn is None:
        return {"Note": "Not supported on this platform in the current build"}
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        return {"Error": f"{type(e).__name__}: {e}"}


def collect_all() -> dict[str, Any]:
    report: dict[str, Any] = {}

    report["Operating System"] = _safe(common.get_os_info)
    report["CPU (overview)"] = _safe(common.get_cpu_basic)
    report["Memory"] = _safe(common.get_memory_info)
    report["Storage (volumes)"] = _safe(common.get_disk_info)
    report["Network (interfaces)"] = _safe(common.get_network_info)
    battery = _safe(common.get_battery_info)
    if battery:
        report["Battery"] = battery
    report["Top Processes (by RAM)"] = _safe(common.get_processes_summary)

    if _plat is not None:
        # CPU detail can be dict (Windows) or list (Linux/macOS)
        cpu_detail = _safe(_plat.get_cpu_detail)
        if isinstance(cpu_detail, dict) and cpu_detail.get("Error"):
            report["CPU (detail)"] = cpu_detail
        elif isinstance(cpu_detail, list):
            report["CPU (detail)"] = cpu_detail
        else:
            report["CPU (detail)"] = cpu_detail
            
        report["GPU"] = _safe(_plat.get_gpu_detail)
        report["Motherboard / BIOS"] = _safe(_plat.get_motherboard_detail)
        
        # Handle chipset function naming differences
        if IS_WINDOWS:
            report["Chipset"] = _safe(_plat.get_chipset_detail)
        else:
            report["Chipset"] = _safe(_plat.get_chipset_hint)
        
        report["Storage (physical/SMART)"] = _safe(_plat.get_storage_detail)
        report["Drivers / Kernel Modules"] = _safe(_plat.get_drivers_detail)
        
        # Platform-specific sections
        if IS_WINDOWS:
            report["RAM Modules"] = _safe(_plat.get_ram_module_detail)
            report["Windows Edition Detail"] = _safe(_plat.get_windows_edition_detail)
            report["BIOS Detail"] = _safe(_plat.get_bios_detailed_info)
            report["EDID / Monitor Info"] = _safe(_plat.get_edid_info)
            report["Battery Detail"] = _safe(_plat.get_battery_detailed_info)
            report["ACPI / SMBIOS"] = _safe(_plat.get_acpi_tables_info)
            report["SMBIOS / DMI"] = _safe(_plat.get_smbios_detailed_info)
            report["PCI / USB Bus"] = _safe(_plat.get_pci_usb_bus_info)
        elif IS_LINUX:
            report["Network Hardware"] = _safe(_plat.get_network_hardware)
        elif IS_MACOS:
            report["BIOS Detail"] = _safe(_plat.get_bios_detailed_info)
            report["Battery Detail"] = _safe(_plat.get_battery_detailed_info)
            report["SMBIOS / DMI"] = _safe(_plat.get_smbios_detailed_info)
            report["Network Hardware"] = _safe(_plat.get_network_hardware)
    else:
        report["Note"] = {
            "Platform": f"Deep hardware tabs are only implemented for Windows, Linux, and macOS. "
                        f"Detected: {platform.system()}. Cross-platform data above still works."
        }

    return report
