"""
windows_info.py — deep hardware detail on Windows 8 / 8.1 / 10 / 11.

IMPORTANT DESIGN NOTE
----------------------
This deliberately talks to the WMI *service* through the `wmi` /
`pywin32` COM bridge (Win32_* classes), NOT the `wmic.exe` command-line
tool. Microsoft deprecated and, on Windows 11 24H2+, removed wmic.exe —
but the underlying WMI service/COM interface it used to wrap is still
fully supported and is the same API PowerShell's `Get-CimInstance` and
tools like HWiNFO/Speccy use. That keeps this working across the whole
Windows 8 → 11 range without relying on a binary Microsoft is retiring.

Requires: pywin32 (`pip install pywin32`) and `wmi` (`pip install wmi`).
Both are Windows-only and imported lazily so this module can still be
*imported* (but not used) on non-Windows platforms without crashing.
"""
from __future__ import annotations

import platform
from typing import Any

# Only import Windows-specific libraries if we're actually on Windows
if platform.system() == "Windows":
    try:
        import wmi  # type: ignore
        _WMI_AVAILABLE = True
    except ImportError:
        _WMI_AVAILABLE = False
else:
    _WMI_AVAILABLE = False


def _get_wmi():
    if not _WMI_AVAILABLE:
        raise RuntimeError("WMI is only available on Windows with pywin32 and wmi installed")
    import wmi  # type: ignore
    return wmi.WMI()


_ARCH_MAP = {0: "x86", 1: "MIPS", 2: "Alpha", 3: "PowerPC", 5: "ARM", 6: "ia64", 9: "x64", 12: "ARM64"}


def get_cpu_detail() -> list[dict[str, Any]]:
    if not _WMI_AVAILABLE:
        return [{"Error": "WMI not available - this function only works on Windows"}]
    
    try:
        c = _get_wmi()
        cpus = []
        for cpu in c.Win32_Processor():
            # Determine if 32-bit or 64-bit
            arch = _ARCH_MAP.get(cpu.Architecture, f"unknown ({cpu.Architecture})")
            is_64bit = arch in ["x64", "ARM64", "ia64"]
            
            # Try to get CPU generation and model info from the name
            cpu_name = cpu.Name.strip() if cpu.Name else "n/a"
            generation_info = _extract_cpu_generation(cpu_name)
            
            cpus.append({
                "Name": cpu_name,
                "Manufacturer": cpu.Manufacturer,
                "Cores": cpu.NumberOfCores,
                "Logical Processors": cpu.NumberOfLogicalProcessors,
                "Max Clock Speed (MHz)": cpu.MaxClockSpeed,
                "Current Clock Speed (MHz)": cpu.CurrentClockSpeed,
                "L2 Cache (KB)": cpu.L2CacheSize,
                "L3 Cache (KB)": cpu.L3CacheSize,
                "L1 Cache (KB)": cpu.L1CacheSize if hasattr(cpu, 'L1CacheSize') else "n/a",
                "Socket": cpu.SocketDesignation,
                "Architecture": arch,
                "CPU Mode": "64-bit" if is_64bit else "32-bit",
                "Address Width": f"{cpu.AddressWidth}-bit" if cpu.AddressWidth else "n/a",
                "Data Width": f"{cpu.DataWidth}-bit" if cpu.DataWidth else "n/a",
                "Voltage (V)": cpu.CurrentVoltage / 10 if cpu.CurrentVoltage else "n/a",
                "Generation/Family": generation_info,
                "Stepping": cpu.Stepping if hasattr(cpu, 'Stepping') else "n/a",
                "Status": cpu.Status,
                "CPU ID": cpu.ProcessorId if hasattr(cpu, 'ProcessorId') else "n/a",
            })
        return cpus
    except Exception as e:
        return [{"Error": f"Failed to get CPU detail: {str(e)}"}]


def _extract_cpu_generation(cpu_name: str) -> str:
    """Extract CPU generation information from the CPU name."""
    if not cpu_name or cpu_name == "n/a":
        return "n/a"
    
    cpu_name_lower = cpu_name.lower()
    
    # Intel processors
    if "intel" in cpu_name_lower:
        if "core i9" in cpu_name_lower:
            return "Intel Core i9 (High-end)"
        elif "core i7" in cpu_name_lower:
            return "Intel Core i7 (High-performance)"
        elif "core i5" in cpu_name_lower:
            return "Intel Core i5 (Mainstream)"
        elif "core i3" in cpu_name_lower:
            return "Intel Core i3 (Entry-level)"
        elif "xeon" in cpu_name_lower:
            return "Intel Xeon (Server/Workstation)"
        elif "pentium" in cpu_name_lower:
            return "Intel Pentium (Budget)"
        elif "celeron" in cpu_name_lower:
            return "Intel Celeron (Entry-level)"
        elif "atom" in cpu_name_lower:
            return "Intel Atom (Low-power)"
        else:
            return "Intel (Unknown generation)"
    
    # AMD processors
    elif "amd" in cpu_name_lower:
        if "ryzen 9" in cpu_name_lower:
            return "AMD Ryzen 9 (High-end)"
        elif "ryzen 7" in cpu_name_lower:
            return "AMD Ryzen 7 (High-performance)"
        elif "ryzen 5" in cpu_name_lower:
            return "AMD Ryzen 5 (Mainstream)"
        elif "ryzen 3" in cpu_name_lower:
            return "AMD Ryzen 3 (Entry-level)"
        elif "threadripper" in cpu_name_lower:
            return "AMD Threadripper (Enthusiast/Workstation)"
        elif "epyc" in cpu_name_lower:
            return "AMD EPYC (Server)"
        elif "athlon" in cpu_name_lower:
            return "AMD Athlon (Budget)"
        elif "fx" in cpu_name_lower:
            return "AMD FX (Legacy)"
        else:
            return "AMD (Unknown generation)"
    
    # ARM processors
    elif "snapdragon" in cpu_name_lower:
        return "Qualcomm Snapdragon (ARM-based)"
    elif "apple" in cpu_name_lower:
        return "Apple Silicon (ARM-based)"
    elif "arm" in cpu_name_lower:
        return "ARM Processor"
    
    return "Unknown CPU generation"


def get_gpu_detail() -> list[dict[str, Any]]:
    if not _WMI_AVAILABLE:
        return [{"Error": "WMI not available - this function only works on Windows"}]
    
    try:
        c = _get_wmi()
        gpus = []
        gpu_index = 0
        for gpu in c.Win32_VideoController():
            gpu_index += 1
            vram = None
            try:
                # AdapterRAM is a 32-bit field and overflows/wraps for GPUs
                # with >4GB VRAM on many driver versions — flag that.
                if gpu.AdapterRAM:
                    vram_gb = round(int(gpu.AdapterRAM) / (1024 ** 3), 2)
                    vram = f"{vram_gb} GB (may be inaccurate above 4GB, WMI limitation)"
            except Exception:
                vram = "n/a"
            
            # Determine GPU type
            gpu_name = gpu.Name.lower() if gpu.Name else ""
            gpu_type = _determine_gpu_type(gpu_name)
            
            gpus.append({
                "GPU #": gpu_index,
                "Name": gpu.Name,
                "GPU Type": gpu_type,
                "Driver Version": gpu.DriverVersion,
                "Driver Date": gpu.DriverDate,
                "VRAM (reported)": vram or "n/a",
                "Current Resolution": f"{gpu.CurrentHorizontalResolution}x{gpu.CurrentVerticalResolution}"
                if gpu.CurrentHorizontalResolution else "n/a",
                "Max Resolution": f"{gpu.MaxRefreshRate} Hz" if gpu.MaxRefreshRate else "n/a",
                "Status": gpu.Status,
                "PNP Device ID": gpu.PNPDeviceID,
                "Installed Display Drivers": gpu.InstalledDisplayDrivers if hasattr(gpu, 'InstalledDisplayDrivers') else "n/a",
                "Driver Model": gpu.DriverModel if hasattr(gpu, 'DriverModel') else "n/a",
            })
        return gpus
    except Exception as e:
        return [{"Error": f"Failed to get GPU detail: {str(e)}"}]


def _determine_gpu_type(gpu_name: str) -> str:
    """Determine if GPU is integrated, discrete, or other type."""
    if not gpu_name:
        return "Unknown"
    
    gpu_name_lower = gpu_name.lower()
    
    # Intel integrated graphics
    if any(intel_igpu in gpu_name_lower for intel_igpu in ["intel", "iris", "uhd", "hd graphics", "uhd graphics"]):
        return "Integrated (Intel)"
    
    # AMD integrated graphics
    elif any(amd_igpu in gpu_name_lower for amd_igpu in ["amd radeon", "radeon graphics", "vega", "rdna"]):
        # Check if it's likely integrated (mobile/APU)
        if any(mobile in gpu_name_lower for mobile in ["mobile", "apu", "notebook", "laptop"]):
            return "Integrated (AMD APU)"
        else:
            return "Discrete (AMD)"
    
    # NVIDIA discrete
    elif "nvidia" in gpu_name_lower or "geforce" in gpu_name_lower or "quadro" in gpu_name_lower or "tesla" in gpu_name_lower:
        return "Discrete (NVIDIA)"
    
    # Other integrated
    elif any(other_igpu in gpu_name_lower for other_igpu in ["integrated", "igpu", "onboard"]):
        return "Integrated (Unknown)"
    
    # Assume discrete for others
    else:
        return "Discrete (Unknown)"


def get_motherboard_detail() -> dict[str, Any]:
    if not _WMI_AVAILABLE:
        return {"Error": "WMI not available - this function only works on Windows"}
    
    try:
        c = _get_wmi()
        result: dict[str, Any] = {}

        boards = c.Win32_BaseBoard()
        if boards:
            b = boards[0]
            result.update({
                "Board Manufacturer": b.Manufacturer,
                "Board Product": b.Product,
                "Board Version": b.Version,
                "Board Serial": b.SerialNumber,
            })

        bios_list = c.Win32_BIOS()
        if bios_list:
            bios = bios_list[0]
            result.update({
                "BIOS Manufacturer": bios.Manufacturer,
                "BIOS Version": ", ".join(bios.BIOSVersion) if bios.BIOSVersion else bios.SMBIOSBIOSVersion,
                "BIOS Release Date": bios.ReleaseDate,
                "BIOS Serial": bios.SerialNumber,
            })

        systems = c.Win32_ComputerSystem()
        if systems:
            s = systems[0]
            result.update({
                "System Manufacturer": s.Manufacturer,
                "System Model": s.Model,
                "System Family": s.SystemFamily,
            })

        return result
    except Exception as e:
        return {"Error": f"Failed to get motherboard detail: {str(e)}"}


def get_chipset_detail() -> dict[str, Any]:
    """
    Windows has no single 'Win32_Chipset' class. The PCI-to-ISA / LPC
    bridge entry on the motherboard's PCI bus is the closest universal
    identifier of the actual chipset southbridge/PCH — same trick tools
    like CPU-Z use under the hood before falling back to their own ID
    database.
    """
    if not _WMI_AVAILABLE:
        return {"Error": "WMI not available - this function only works on Windows"}
    
    try:
        c = _get_wmi()
        result = {}
        
        # Try to find PCH/Southbridge
        for dev in c.Win32_PnPEntity():
            try:
                if dev.PNPClass == "System" and dev.Name and (
                    "LPC" in dev.Name or "ISA Bridge" in dev.Name or "PCH" in dev.Name
                ):
                    result["Southbridge/PCH"] = dev.Name
                    result["PCH Device ID"] = dev.DeviceID
                    break
            except Exception:
                continue
        
        # Try to find Northbridge (though less common in modern systems)
        for dev in c.Win32_PnPEntity():
            try:
                if dev.PNPClass == "System" and dev.Name and (
                    "Northbridge" in dev.Name or "Memory Controller" in dev.Name or "Host Bridge" in dev.Name
                ):
                    result["Northbridge"] = dev.Name
                    result["Northbridge Device ID"] = dev.DeviceID
                    break
            except Exception:
                continue
        
        # Try to get chipset manufacturer from motherboard info
        try:
            boards = c.Win32_BaseBoard()
            if boards:
                result["Chipset Manufacturer"] = boards[0].Manufacturer
        except Exception:
            pass
        
        if not result:
            return {"Chipset": "Not identifiable via WMI PnP enumeration on this system"}
        
        return result
    except Exception as e:
        return {"Error": f"Failed to get chipset detail: {str(e)}"}


def get_storage_detail() -> list[dict[str, Any]]:
    if not _WMI_AVAILABLE:
        return [{"Error": "WMI not available - this function only works on Windows"}]
    
    try:
        c = _get_wmi()
        disks = []
        for disk in c.Win32_DiskDrive():
            # Determine storage type
            storage_type = _determine_storage_type(disk)
            
            disks.append({
                "Model": disk.Model,
                "Interface Type": disk.InterfaceType,
                "Size (GB)": round(int(disk.Size) / (1024 ** 3), 2) if disk.Size else "n/a",
                "Media Type": disk.MediaType,
                "Storage Type": storage_type,
                "Serial Number": (disk.SerialNumber or "n/a").strip(),
                "Partitions": disk.Partitions,
                "Status": disk.Status,
                "Firmware Revision": disk.FirmwareRevision if hasattr(disk, 'FirmwareRevision') else "n/a",
                "Bytes per Sector": disk.BytesPerSector if hasattr(disk, 'BytesPerSector') else "n/a",
                "Sectors per Track": disk.SectorsPerTrack if hasattr(disk, 'SectorsPerTrack') else "n/a",
                "Tracks per Cylinder": disk.TracksPerCylinder if hasattr(disk, 'TracksPerCylinder') else "n/a",
                "Cylinders": disk.TotalCylinders if hasattr(disk, 'TotalCylinders') else "n/a",
                "Media Type Desc": _get_media_type_description(disk.MediaType),
            })
        return disks
    except Exception as e:
        return [{"Error": f"Failed to get storage detail: {str(e)}"}]


def _determine_storage_type(disk) -> str:
    """Determine if storage is SSD, HDD, USB, CD, floppy, etc."""
    if not disk:
        return "Unknown"
    
    model = disk.Model.lower() if disk.Model else ""
    media_type = disk.MediaType.lower() if disk.MediaType else ""
    interface = disk.InterfaceType.lower() if disk.InterfaceType else ""
    
    # Check for SSD
    if any(ssd_indicator in model for ssd_indicator in ["ssd", "solid state"]):
        return "SSD (Solid State Drive)"
    
    # Check for USB storage
    if "usb" in interface or "removable" in media_type:
        return "USB Storage"
    
    # Check for CD/DVD
    if any(cd_indicator in model for cd_indicator in ["cd-rom", "dvd", "bd-rom", "blu-ray", "optical"]):
        return "Optical Drive (CD/DVD/Blu-ray)"
    
    # Check for floppy
    if any(floppy_indicator in model for floppy_indicator in ["floppy", "floppy disk"]):
        return "Floppy Drive"
    
    # Check for HDD
    if any(hdd_indicator in model for hdd_indicator in ["hdd", "hard disk", "wd", "seagate", "toshiba", "hitachi"]):
        return "HDD (Hard Disk Drive)"
    
    # Check for NVMe
    if "nvme" in interface or "nvme" in model:
        return "NVMe SSD"
    
    # Default to HDD for most traditional spinning disks
    if interface in ["scsi", "ata", "sata", "sas"]:
        return "HDD (likely)"
    
    return "Unknown Storage Type"


def _get_media_type_description(media_type: str) -> str:
    """Get a more descriptive media type."""
    if not media_type:
        return "n/a"
    
    media_lower = media_type.lower()
    
    if "fixed" in media_lower or "hard" in media_lower:
        return "Fixed hard disk media"
    elif "removable" in media_lower:
        return "Removable media"
    elif "optical" in media_lower or "cd" in media_lower or "dvd" in media_lower:
        return "Optical disc"
    elif "floppy" in media_lower:
        return "Floppy disk"
    else:
        return media_type


def get_drivers_detail(limit: int = 50) -> list[dict[str, Any]]:
    """Signed driver inventory — the direct Windows equivalent of `lsmod`."""
    if not _WMI_AVAILABLE:
        return [{"Error": "WMI not available - this function only works on Windows"}]
    
    try:
        c = _get_wmi()
        drivers = []
        for drv in c.Win32_PnPSignedDriver():
            driver_info = {
                "Device Name": drv.DeviceName,
                "Driver Version": drv.DriverVersion,
                "Manufacturer": drv.Manufacturer,
                "Driver Date": drv.DriverDate,
                "Is Signed": drv.IsSigned,
                "Class": drv.DeviceClass,
                "Driver Provider": drv.DriverProviderName if hasattr(drv, 'DriverProviderName') else "n/a",
                "Inf Name": drv.InfName if hasattr(drv, 'InfName') else "n/a",
                "Device ID": drv.DeviceID if hasattr(drv, 'DeviceID') else "n/a",
            }
            drivers.append(driver_info)
            if len(drivers) >= limit:
                break
        return drivers
    except Exception as e:
        return [{"Error": f"Failed to get drivers detail: {str(e)}"}]


def get_ram_module_detail() -> list[dict[str, Any]]:
    """Per-stick RAM info via SMBIOS Type 17 (speed, slot, manufacturer)."""
    if not _WMI_AVAILABLE:
        return [{"Error": "WMI not available - this function only works on Windows"}]
    
    try:
        c = _get_wmi()
        sticks = []
        total_slots = 0
        populated_slots = 0
        
        # Get all physical memory
        memory_devices = list(c.Win32_PhysicalMemory())
        populated_slots = len(memory_devices)
        
        # Try to get total number of memory slots
        try:
            memory_arrays = c.Win32_PhysicalMemoryArray()
            if memory_arrays:
                for mem_array in memory_arrays:
                    if hasattr(mem_array, 'MemoryDevices') and mem_array.MemoryDevices:
                        total_slots = mem_array.MemoryDevices
                        break
        except Exception:
            total_slots = populated_slots  # Fallback to count of populated slots
        
        for mem in memory_devices:
            # Determine memory type
            mem_type = _get_memory_type_name(mem.SMBIOSMemoryType)
            
            stick_info = {
                "Slot": mem.DeviceLocator,
                "Bank Label": mem.BankLabel if hasattr(mem, 'BankLabel') else "n/a",
                "Capacity (GB)": round(int(mem.Capacity) / (1024 ** 3), 2) if mem.Capacity else "n/a",
                "Speed (MHz)": mem.Speed,
                "Manufacturer": mem.Manufacturer,
                "Part Number": (mem.PartNumber or "n/a").strip(),
                "Memory Type": mem_type,
                "Serial Number": mem.SerialNumber if hasattr(mem, 'SerialNumber') else "n/a",
                "Configured Clock Speed": mem.ConfiguredClockSpeed if hasattr(mem, 'ConfiguredClockSpeed') else "n/a",
                "Slot Population": f"{len(sticks) + 1} of {total_slots}" if total_slots > 0 else "n/a",
            }
            sticks.append(stick_info)
        
        # Add summary as a separate item
        if total_slots > 0:
            summary = {
                "Summary": {
                    "Total Slots": total_slots,
                    "Populated Slots": populated_slots,
                    "Empty Slots": total_slots - populated_slots,
                    "Slot Population": f"{populated_slots} of {total_slots}",
                    "Total Capacity (GB)": sum(s.get("Capacity (GB)", 0) for s in sticks if isinstance(s.get("Capacity (GB)"), (int, float)))
                }
            }
            sticks.append(summary)
        
        return sticks
    except Exception as e:
        return [{"Error": f"Failed to get RAM module detail: {str(e)}"}]


def _get_memory_type_name(smbios_type: int) -> str:
    """Convert SMBIOS memory type code to human-readable name."""
    memory_types = {
        0: "Unknown",
        1: "Other",
        2: "DRAM",
        3: "EDRAM",
        4: "VRAM",
        5: "Flash",
        6: "EEPROM",
        7: "EPROM",
        8: "ROM",
        9: "Flash EPROM",
        10: "EEPROM",
        11: "FEPROM",
        12: "EPROM",
        13: "CDRAM",
        14: "3DRAM",
        15: "SDRAM",
        16: "SGRAM",
        17: "RDRAM",
        18: "DDR",
        19: "DDR2",
        20: "DDR2 FB-DIMM",
        21: "DDR3",
        22: "FBD2",
        23: "DDR4",
        24: "LPDDR",
        25: "DDR3",
        26: "DDR4",
        27: "DDR5",
        28: "LPDDR2",
        29: "LPDDR3",
        30: "LPDDR4",
        31: "LPDDR5",
    }
    return memory_types.get(smbios_type, f"Unknown ({smbios_type})")


def get_windows_edition_detail() -> dict[str, Any]:
    """Extra Windows-specific OS detail beyond what platform.uname() gives."""
    if not _WMI_AVAILABLE:
        return {"Error": "WMI not available - this function only works on Windows"}
    
    try:
        c = _get_wmi()
        os_list = c.Win32_OperatingSystem()
        if not os_list:
            return {}
        o = os_list[0]
        return {
            "Caption": o.Caption,
            "Build Number": o.BuildNumber,
            "OS Architecture": o.OSArchitecture,
            "Install Date": o.InstallDate,
            "Registered User": o.RegisteredUser,
            "Serial Number": o.SerialNumber,
            "Windows Directory": o.WindowsDirectory,
        }
    except Exception as e:
        return {"Error": f"Failed to get Windows edition detail: {str(e)}"}


def get_bios_detailed_info() -> dict[str, Any]:
    """Detailed BIOS information including age and features."""
    if not _WMI_AVAILABLE:
        return {"Error": "WMI not available - this function only works on Windows"}
    
    try:
        c = _get_wmi()
        result = {}
        
        bios_list = c.Win32_BIOS()
        if bios_list:
            bios = bios_list[0]
            result.update({
                "BIOS Manufacturer": bios.Manufacturer,
                "BIOS Version": ", ".join(bios.BIOSVersion) if bios.BIOSVersion else bios.SMBIOSBIOSVersion,
                "BIOS Release Date": bios.ReleaseDate,
                "BIOS Serial": bios.SerialNumber,
                "SMBIOS Version": bios.SMBIOSMajorVersion if hasattr(bios, 'SMBIOSMajorVersion') else "n/a",
                "SMBIOS Minor Version": bios.SMBIOSMinorVersion if hasattr(bios, 'SMBIOSMinorVersion') else "n/a",
                "BIOS Age": _calculate_bios_age(bios.ReleaseDate) if bios.ReleaseDate else "n/a",
            })
        
        # Get BIOS characteristics
        try:
            for bios in c.Win32_BIOS():
                if hasattr(bios, 'BIOSCharacteristics') and bios.BIOSCharacteristics:
                    result["BIOS Characteristics"] = bios.BIOSCharacteristics
                break
        except Exception:
            pass
        
        return result
    except Exception as e:
        return {"Error": f"Failed to get BIOS detail: {str(e)}"}


def _calculate_bios_age(release_date: str) -> str:
    """Calculate BIOS age from release date."""
    try:
        if not release_date or release_date == "n/a":
            return "n/a"
        
        # WMI dates are in CIM_DATETIME format: YYYYMMDDHHMMSS.mmmmmm+XXX
        if len(release_date) >= 8:
            year = int(release_date[:4])
            month = int(release_date[4:6])
            day = int(release_date[6:8])
            
            from datetime import datetime
            bios_date = datetime(year, month, day)
            current_date = datetime.now()
            age_days = (current_date - bios_date).days
            
            if age_days < 30:
                return f"{age_days} days old (Recent)"
            elif age_days < 365:
                months = age_days // 30
                return f"{months} months old"
            elif age_days < 365 * 3:
                years = age_days // 365
                return f"{years} year(s) old (Moderate)"
            else:
                years = age_days // 365
                return f"{years} year(s) old (Old)"
    except Exception:
        return "Unable to calculate"
    
    return "n/a"


def get_edid_info() -> dict[str, Any]:
    """Get Extended Display Identification Data (EDID) for monitors."""
    if not _WMI_AVAILABLE:
        return {"Error": "WMI not available - this function only works on Windows"}
    
    try:
        c = _get_wmi()
        monitors = []
        
        for monitor in c.Win32_DesktopMonitor():
            if monitor.Name and monitor.Name != "Default Monitor":
                monitor_info = {
                    "Monitor Name": monitor.Name,
                    "Monitor Type": monitor.MonitorType if hasattr(monitor, 'MonitorType') else "n/a",
                    "Screen Height": monitor.ScreenHeight if hasattr(monitor, 'ScreenHeight') else "n/a",
                    "Screen Width": monitor.ScreenWidth if hasattr(monitor, 'ScreenWidth') else "n/a",
                    "PNP Device ID": monitor.PNPDeviceID if hasattr(monitor, 'PNPDeviceID') else "n/a",
                }
                monitors.append(monitor_info)
        
        if not monitors:
            return {"Note": "No detailed EDID information available via WMI"}
        
        return {"Monitors": monitors}
    except Exception as e:
        return {"Error": f"Could not retrieve EDID info: {str(e)}"}


def get_battery_detailed_info() -> dict[str, Any]:
    """Detailed battery information including wear level."""
    if not _WMI_AVAILABLE:
        return {"Error": "WMI not available - this function only works on Windows"}
    
    try:
        c = _get_wmi()
        result = {}
        
        battery = c.Win32_Battery()
        if battery:
            bat = battery[0]
            result.update({
                "Battery Name": bat.Name if hasattr(bat, 'Name') else "n/a",
                "Battery Status": bat.BatteryStatus if hasattr(bat, 'BatteryStatus') else "n/a",
                "Estimated Charge Remaining (%)": bat.EstimatedChargeRemaining if hasattr(bat, 'EstimatedChargeRemaining') else "n/a",
                "Design Capacity": bat.DesignCapacity if hasattr(bat, 'DesignCapacity') else "n/a",
                "Full Charge Capacity": bat.FullChargeCapacity if hasattr(bat, 'FullChargeCapacity') else "n/a",
                "Chemistry": bat.Chemistry if hasattr(bat, 'Chemistry') else "n/a",
                "Manufacture Date": bat.ManufactureDate if hasattr(bat, 'ManufactureDate') else "n/a",
            })
            
            # Calculate wear level if we have both capacities
            if hasattr(bat, 'DesignCapacity') and hasattr(bat, 'FullChargeCapacity') and bat.DesignCapacity and bat.FullChargeCapacity:
                try:
                    design_cap = int(bat.DesignCapacity)
                    full_charge_cap = int(bat.FullChargeCapacity)
                    if design_cap > 0:
                        wear_level = ((design_cap - full_charge_cap) / design_cap) * 100
                        result["Wear Level"] = f"{wear_level:.1f}%"
                        result["Health"] = f"{100 - wear_level:.1f}%"
                except Exception:
                    pass
        
        if not result:
            return {"Note": "No battery detected or no detailed battery information available"}
        
        return result
    except Exception as e:
        return {"Error": f"Could not retrieve battery info: {str(e)}"}


def get_acpi_tables_info() -> dict[str, Any]:
    """Get ACPI table information."""
    if not _WMI_AVAILABLE:
        return {"Error": "WMI not available - this function only works on Windows"}
    
    try:
        c = _get_wmi()
        result = {}
        
        # Try to get system enclosure information (part of ACPI/SMBIOS)
        enclosure = c.Win32_SystemEnclosure()
        if enclosure:
            enc = enclosure[0]
            result.update({
                "Chassis Types": enc.ChassisTypes if hasattr(enc, 'ChassisTypes') else "n/a",
                "Manufacturer": enc.Manufacturer if hasattr(enc, 'Manufacturer') else "n/a",
                "Model": enc.Model if hasattr(enc, 'Model') else "n/a",
                "Serial Number": enc.SerialNumber if hasattr(enc, 'SerialNumber') else "n/a",
                "SMBIOS Asset Tag": enc.SMBIOSAssetTag if hasattr(enc, 'SMBIOSAssetTag') else "n/a",
            })
        
        if not result:
            return {"Note": "Limited ACPI table information available via WMI"}
        
        return result
    except Exception as e:
        return {"Error": f"Could not retrieve ACPI/SMBIOS info: {str(e)}"}


def get_smbios_detailed_info() -> dict[str, Any]:
    """Get detailed SMBIOS/DMI information."""
    if not _WMI_AVAILABLE:
        return {"Error": "WMI not available - this function only works on Windows"}
    
    try:
        c = _get_wmi()
        result = {}
        
        # Get computer system information
        computer = c.Win32_ComputerSystem()
        if computer:
            comp = computer[0]
            result.update({
                "System Manufacturer": comp.Manufacturer,
                "System Model": comp.Model,
                "System Type": comp.SystemType if hasattr(comp, 'SystemType') else "n/a",
                "System Family": comp.SystemFamily if hasattr(comp, 'SystemFamily') else "n/a",
                "Number of Processors": comp.NumberOfProcessors if hasattr(comp, 'NumberOfProcessors') else "n/a",
            })
        
        # Get base board information
        baseboard = c.Win32_BaseBoard()
        if baseboard:
            board = baseboard[0]
            result.update({
                "Board Manufacturer": board.Manufacturer,
                "Board Product": board.Product,
                "Board Version": board.Version,
                "Board Serial": board.SerialNumber,
            })
        
        # Get BIOS information
        bios = c.Win32_BIOS()
        if bios:
            b = bios[0]
            result.update({
                "BIOS Version": b.SMBIOSBIOSVersion,
                "BIOS Release Date": b.ReleaseDate,
                "SMBIOS Version": f"{b.SMBIOSMajorVersion}.{b.SMBIOSMinorVersion}" if hasattr(b, 'SMBIOSMajorVersion') else "n/a",
            })
        
        if not result:
            return {"Note": "No SMBIOS information available"}
        
        return result
    except Exception as e:
        return {"Error": f"Could not retrieve SMBIOS info: {str(e)}"}


def get_pci_usb_bus_info() -> dict[str, Any]:
    """Get PCI and USB bus information."""
    if not _WMI_AVAILABLE:
        return {"Error": "WMI not available - this function only works on Windows"}
    
    try:
        c = _get_wmi()
        result = {"PCI Devices": [], "USB Controllers": []}
        
        # Get PCI devices (limited to prevent performance issues)
        pci_count = 0
        for dev in c.Win32_PnPEntity():
            try:
                if dev.PNPClass and "PCI" in dev.PNPClass.upper():
                    pci_info = {
                        "Name": dev.Name,
                        "Device ID": dev.DeviceID,
                        "Manufacturer": dev.Manufacturer if hasattr(dev, 'Manufacturer') else "n/a",
                        "Status": dev.Status if hasattr(dev, 'Status') else "n/a",
                    }
                    result["PCI Devices"].append(pci_info)
                    pci_count += 1
                    if pci_count >= 20:  # Limit to 20 PCI devices
                        break
            except Exception:
                continue
        
        # Get USB controllers (limited to prevent performance issues)
        usb_count = 0
        for dev in c.Win32_PnPEntity():
            try:
                if dev.PNPClass and "USB" in dev.PNPClass.upper():
                    usb_info = {
                        "Name": dev.Name,
                        "Device ID": dev.DeviceID,
                        "Manufacturer": dev.Manufacturer if hasattr(dev, 'Manufacturer') else "n/a",
                        "Status": dev.Status if hasattr(dev, 'Status') else "n/a",
                    }
                    result["USB Controllers"].append(usb_info)
                    usb_count += 1
                    if usb_count >= 15:  # Limit to 15 USB controllers
                        break
            except Exception:
                continue
        
        if not result["PCI Devices"] and not result["USB Controllers"]:
            return {"Note": "No PCI/USB bus information available"}
        
        return result
    except Exception as e:
        return {"Error": f"Could not retrieve PCI/USB info: {str(e)}"}
