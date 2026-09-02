# System Info Tool

A cross-platform (Windows 8/8.1/10/11 + Linux + macOS) hardware & OS
information dashboard — CPU, GPU, motherboard, chipset, storage,
drivers, memory, network, battery, processes — with a one-click HTML
report export and email sharing, and an optional fully portable mode
(no install, runs off a USB stick, no state left on the host machine).

It's built in the same spirit as tools like PC Internals / HWiNFO /
TMOG, but focused on **full static + point-in-time info you can export
and share**, rather than a 60fps live performance HUD (see "Why not a
live 60Hz monitor?" below for why that's a deliberate choice, not a
missing feature).

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

### 🔍 Comprehensive Hardware Detection
- **CPU**: Detailed processor information including architecture, cores, cache, clock speeds, and generation detection
- **GPU**: Graphics card details with VRAM, driver versions, and integrated/discrete classification
- **Memory**: RAM modules with slot population, capacity per slot, memory type (DDR4/DDR5), and manufacturer info
- **Storage**: Physical drives with SSD/HDD detection, SMART health, interface types, and detailed specs
- **Motherboard**: Board manufacturer, BIOS details, chipset information (Northbridge/Southbridge/PCH)
- **Network**: Interface details, hardware info, and MAC addresses
- **Drivers**: Signed driver inventory (Windows) or kernel modules (Linux)
- **Battery**: Battery health, wear level, and detailed status information

### 🌐 Cross-Platform Support
- **Windows**: WMI-based deep hardware detection with pywin32
- **Linux**: /proc and /sys filesystem access with lspci/dmidecode support
- **macOS**: system_profiler integration for Apple Silicon and Intel Macs

### 🎨 Modern UI
- Built with customtkinter for a modern, dark-themed interface
- Tabbed interface for organized information display
- Export to HTML reports with one click
- Email sharing capability
- Portable mode support (no installation required)

## Running it

```bash
pip install -r requirements.txt
python main.py
```

On Linux, a few CLI tools make the hardware tabs much more detailed if
installed (all optional — the app works without them, just with fewer
fields filled in):

```bash
# Debian/Ubuntu
sudo apt install pciutils util-linux smartmontools
# Fedora
sudo dnf install pciutils util-linux smartmontools
# Arch
sudo pacman -S pciutils util-linux smartmontools
```

On Windows, `pywin32` + `wmi` (in requirements.txt) are all that's
needed — no extra system tools required, and no admin rights either,
for everything except a few storage/driver fields that Windows itself
restricts to elevated processes.

## What's in each tab

| Tab | Windows source | Linux source |
|---|---|---|
| Overview | `platform`, `psutil` | same |
| CPU | `Win32_Processor` (WMI) | `/proc/cpuinfo`, `/sys/.../cpufreq`, thermal zones |
| GPU | `Win32_VideoController` (WMI) | `lspci` (+ `nvidia-smi` if present) |
| Motherboard | `Win32_BaseBoard` + `Win32_BIOS` (WMI) | `/sys/class/dmi/id/*` |
| Chipset | PCH/LPC bridge entry via WMI PnP enum | PCI host/ISA bridge entry via `lspci` |
| Storage | `Win32_DiskDrive` (WMI) | `lsblk` + `smartctl -H` if installed |
| Drivers | `Win32_PnPSignedDriver` (WMI) | `lsmod` / `/proc/modules` |
| RAM modules | `Win32_PhysicalMemory` (SMBIOS Type 17) | *(no universal per-stick API without root `dmidecode`; falls back to totals)* |
| Network | `psutil` | `psutil` + `lspci` for NIC hardware |

Every probe is wrapped so a single missing tool, missing permission,
or unsupported Windows build never crashes the app — that field just
shows a plain-language note instead ("needs root", "smartmontools not
installed", etc.) and everything else keeps working.

## Why WMI (not `wmic.exe`) on Windows

Microsoft deprecated `wmic.exe` and removed it entirely starting with
Windows 11 24H2. This app never shells out to it. Instead it talks
straight to the **WMI service** through the `wmi`/`pywin32` COM
bridge — the same underlying API PowerShell's `Get-CimInstance` and
tools like HWiNFO use — so it keeps working across the full Windows
8 → 11 range without depending on a binary Microsoft is retiring.

## Portable mode

Drop a file named `portable.flag` (empty file, any content) next to
the executable/script. When present:

- Settings and the default export folder become a `data/` folder next
  to the executable, instead of `%APPDATA%` / `~/.config`.
- Nothing is written anywhere else on the host machine.

This is the same convention used by well-known portable Windows apps
(7-Zip Portable, Notepad++ Portable, etc.), so it behaves the way
people already expect from a "portable" build.

## Exporting & sharing a report

**Export HTML Report** renders everything currently collected into a
single self-contained, dark-themed HTML file (see `report.py` /
`build_html_report`) — no external assets, safe to email or upload
anywhere, opens in any browser.

**Share via Email** has two modes:

1. **Default (no setup needed):** opens the OS's own default mail
   client with a prefilled draft pointing at the exported file. You
   review and attach it yourself before sending — no credentials ever
   touch this app.
2. **Optional direct send:** if you fill in your own SMTP server +
   login under *Settings*, the app can send the HTML report directly
   as the email body. This is entirely opt-in — the app ships with no
   mail server configured and never sends anything on its own.

   ⚠️ SMTP credentials are currently stored in plain JSON in the
   settings file (see `portable.py` / `save_settings`). For a personal
   machine or a portable USB build that's usually an acceptable
   trade-off, but if you want stronger protection, wire in the
   `keyring` package (OS credential vault) instead — that's a natural
   next step, not currently implemented.

## Packaging as a portable executable

### Windows

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed --name SystemInfoTool main.py
# creates dist\SystemInfoTool.exe

# To make it portable:
copy nul dist\portable.flag
# ship dist\SystemInfoTool.exe + dist\portable.flag together
# (same folder, e.g. on a USB stick)
```

`--windowed` suppresses the console window since this is a GUI app.
Test the built .exe on the oldest Windows version you need to support
(8/8.1) — `customtkinter` and `pywin32` both support back to Windows 7,
so this should Just Work, but always verify on real hardware/VMs before
distributing.

### Linux

```bash
pip install pyinstaller
pyinstaller --onefile --name SystemInfoTool main.py
# creates dist/SystemInfoTool

chmod +x dist/SystemInfoTool
touch dist/portable.flag
# ship dist/SystemInfoTool + dist/portable.flag together
```

Build on the oldest glibc / distro you need to support, since
PyInstaller Linux builds aren't fully glibc-version-portable across
distros the way the Windows build is across Windows versions — building
on something like Ubuntu 20.04 or a manylinux container gives the
widest compatibility.

## Building a proper Windows installer (Inno Setup)

`SystemInfoTool.iss` builds a normal `SystemInfoTool-Setup.exe`
installer (Start Menu shortcut, optional desktop icon, clean
uninstall) around the PyInstaller build — for when you want a regular
installed app rather than the portable USB-stick build.

1. Build the exe first: run `build_windows_exe.bat` (or PyInstaller
   manually), so `dist\SystemInfoTool.exe` exists.
2. Install [Inno Setup](https://jrsoftware.org/isinfo.php) if you
   don't have it.
3. Either re-run `build_windows_exe.bat` (it auto-detects `ISCC.exe`
   and compiles the installer for you), or open `SystemInfoTool.iss`
   in the Inno Setup Compiler and press **Build**.
4. Output: `Output\SystemInfoTool-Setup.exe`.

This installed build intentionally does **not** ship `portable.flag`
— it installs per-user (no admin rights needed) and stores settings
under `%APPDATA%\SystemInfoTool`, uninstalling cleanly afterwards. Use
the separate portable ZIP (exe + `portable.flag` together, no
installer) for the run-from-USB-stick use case instead.

## Why not a live 60Hz monitor (like TMOG)?

TMOG's whole design point is a live, 60fps-animated performance
cockpit for CPU/RAM/disk graphs while you work — that calls for a
native C++/Qt/Direct2D renderer sampling the kernel many times a
second, which is a fundamentally different (and much larger) project
than a hardware/OS **information** tool. This app instead optimizes
for the PC-Internals-style job: pull a complete, accurate snapshot of
what's *in* the machine and let you export/share it, refreshed on
demand rather than animated continuously. `psutil.cpu_percent(interval=..)`
already gives live-enough numbers for that; wiring up an actual 60Hz
graphing engine would be a good follow-up project built on top of the
same `collectors/` data layer.

## Extending it

Everything the GUI displays comes from `collectors/aggregate.py`'s
`collect_all()`, which returns one flat dict of
`{section_name: data}`. To add a new tab/section:

1. Add a `get_x_detail()` function to `collectors/windows_info.py`
   and/or `collectors/linux_info.py`.
2. Wire it into `collect_all()` in `collectors/aggregate.py`.
3. Add its section name to a tab (or a new tab) in `TAB_ORDER` in
   `main.py`.

The HTML report renderer (`report.py`) and the GUI panel renderer
(`main.py` / `_flatten_for_display`) both walk the data generically —
nested dicts and lists of dicts render automatically, so a new section
needs no changes to either renderer.
