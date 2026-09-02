# System Info Tool

A cross-platform (Windows 8/8.1/10/11 + Linux + macOS) hardware and OS information dashboard with advanced detection capabilities and real-time data collection.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
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

### ⚡ Performance Optimized
- Background data collection to keep UI responsive
- Configurable row limits for large datasets
- Lazy tab rendering for instant startup
- Graceful degradation when system tools are unavailable

## Screenshots

*Add screenshots of the application in action*

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
python main.py
```

## Building Executables

### PyInstaller (Cross-Platform)
```bash
python build.py
```

### Windows Installer (Inno Setup)
```bash
build_installer.bat
```

### Qt Installer Framework (Cross-Platform)
```bash
build_qt_installer.bat
```

For detailed build instructions, see [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md).

## Usage

### Basic Usage
1. Launch the application
2. Click "Refresh" to collect system information
3. Navigate through tabs to view different hardware categories
4. Click "Export HTML Report" to save detailed system information
5. Use "Share via Email" to share system information

### Portable Mode
Create a file named `portable.flag` in the same directory as the executable to enable portable mode. Settings and data will be stored locally instead of in user directories.

## Platform-Specific Features

### Windows
- Deep WMI hardware detection
- Detailed signed driver information
- ACPI/SMBIOS table access
- EDID monitor information
- PCI/USB bus enumeration

### Linux
- /proc and /sys filesystem access
- lspci/dmidecode integration
- Kernel module information
- SMART disk health monitoring
- Thermal zone monitoring

### macOS
- system_profiler integration
- kextstat driver information
- Battery health and cycle count
- Firmware version information
- Hardware UUID detection

## Data Collection

The tool collects real hardware information from system APIs:

- **Windows**: WMI (Windows Management Instrumentation)
- **Linux**: /proc, /sys, and system tools (lspci, dmidecode, smartctl)
- **macOS**: system_profiler and system commands

All data collection is done with proper error handling and graceful degradation when specific tools or permissions are unavailable.

## Configuration

### Settings File
Settings are stored in:
- **Windows**: `%APPDATA%\SystemInfoTool\settings.json`
- **Linux**: `~/.config/SystemInfoTool/settings.json`
- **macOS**: `~/Library/Application Support/SystemInfoTool/settings.json`
- **Portable mode**: `data/settings.json` (next to executable)

### Available Settings
- Default export directory
- Email sharing configuration
- SMTP settings for direct email sending (optional)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [customtkinter](https://github.com/TomSchimansky/CustomTkinter)
- System information via [psutil](https://github.com/giampaolo/psutil)
- Windows hardware detection via [pywin32](https://github.com/mhammond/pywin32) and [wmi](https://github.com/texhnolyze/wmi-wrapper)
- Inspired by tools like CPU-Z, HWiNFO, and PC Internals

## Roadmap

- [ ] Live performance monitoring (CPU/RAM graphs)
- [ ] Network traffic monitoring
- [ ] Temperature monitoring with alerts
- [ ] Custom report templates
- [ ] Command-line interface
- [ ] Web-based interface
- [ ] Hardware comparison database
- [ ] System health scoring

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for build-related questions

## Changelog

### Version 1.0.0
- Initial release
- Cross-platform support (Windows, Linux, macOS)
- Enhanced hardware detection
- Modern UI with customtkinter
- HTML report export
- Email sharing
- Portable mode support
- PyInstaller + Qt Installer Framework build system