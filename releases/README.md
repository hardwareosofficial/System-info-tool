# System Info Tool - Release Builds

This directory contains release builds for different platforms.

## Platform-Specific Releases

### Windows
- **Location**: `windows/`
- **Status**: ✅ Built and ready
- **Files**: 
  - `SystemInfoTool.exe` - Main executable (14.5 MB)
  - `portable.flag` - Enable portable mode
  - `README.txt` - Installation instructions
- **Usage**: Run `SystemInfoTool.exe` directly or use portable mode with `portable.flag`

### Linux
- **Location**: `linux/`
- **Status**: 🔧 Build script provided
- **Files**:
  - `build_linux.sh` - Build script for Linux
  - `README.txt` - Build and installation instructions
- **Usage**: Run `build_linux.sh` on a Linux system to build the executable

### macOS
- **Location**: `macos/`
- **Status**: 🔧 Build script provided
- **Files**:
  - `build_macos.sh` - Build script for macOS
  - `README.txt` - Build and installation instructions
- **Usage**: Run `build_macos.sh` on a Mac to build the executable

## Building Platform-Specific Versions

### Windows (Already Built)
The Windows version is already built and ready in the `windows/` directory.

### Linux (Requires Linux System)
```bash
cd linux
chmod +x build_linux.sh
./build_linux.sh
```

### macOS (Requires Mac)
```bash
cd macos
chmod +x build_macos.sh
./build_macos.sh
```

## Features Available

All platform builds include:
- ✅ Comprehensive hardware detection
- ✅ Modern dark-themed UI
- ✅ Export to HTML reports
- ✅ Email sharing capability
- ✅ Portable mode support
- ✅ Performance optimizations
- ✅ Cross-platform architecture

## Platform-Specific Features

### Windows Features
- WMI-based deep hardware detection
- Detailed signed driver information
- ACPI/SMBIOS table access
- EDID monitor information
- PCI/USB bus enumeration

### Linux Features
- /proc and /sys filesystem access
- lspci/dmidecode integration
- Kernel module information
- SMART disk health monitoring
- Thermal zone monitoring

### macOS Features
- system_profiler integration
- kextstat driver information
- Battery health and cycle count
- Firmware version information
- Apple Silicon support

## Distribution

### Windows Distribution
- Provide the `windows/` folder contents as a ZIP file
- Users can run directly without installation
- Portable mode enabled by default with `portable.flag`

### Linux Distribution
- Provide the source code with build instructions
- Or build Linux executables on target distributions
- Consider creating distribution-specific builds

### macOS Distribution
- Provide the source code with build instructions
- Build on macOS for distribution
- Consider code signing for broader compatibility

## Version Information

Current Version: 1.0.0
Release Date: 2026-09-02
Python Version: 3.14.7
Build System: PyInstaller 6.22.2

## Support

For issues or questions:
- GitHub: https://github.com/hardwareosofficial/System-info-tool
- Issues: https://github.com/hardwareosofficial/System-info-tool/issues

## License

MIT License - See LICENSE file in the root directory.