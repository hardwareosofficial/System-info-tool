System Info Tool - Linux Release
===================================

## Building the Linux Version

Since Linux builds require a Linux environment, you need to build the executable on a Linux system.

### Prerequisites
- Python 3.8 or higher
- pip package manager
- System tools (optional but recommended):
  - pciutils (for GPU info)
  - util-linux (for storage info)
  - smartmontools (for disk health)

### Build Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/hardwareosofficial/System-info-tool.git
   cd System-info-tool
   ```

2. Run the build script:
   ```bash
   chmod +x build_linux.sh
   ./build_linux.sh
   ```

3. Or build manually:
   ```bash
   pip3 install -r requirements.txt
   pip3 install pyinstaller
   python3 -m PyInstaller --onefile --name=SystemInfoTool --add-data="collectors:collectors" --hidden-import=customtkinter --hidden-import=PIL main.py
   chmod +x dist/SystemInfoTool
   touch dist/portable.flag
   ```

### Output
The built executable will be in the `dist/` directory:
- `dist/SystemInfoTool` - Main executable
- `dist/portable.flag` - Enable portable mode

## Running the Application

### Standard Installation
```bash
./dist/SystemInfoTool
```

### Portable Mode
1. Keep both SystemInfoTool and portable.flag in the same folder
2. Run: `./SystemInfoTool`
3. Settings and data will be stored in a 'data' folder next to the executable

## Linux-Specific Features
- /proc and /sys filesystem access for hardware info
- lspci integration for GPU detection
- dmidecode support for detailed system info
- Kernel module information
- SMART disk health monitoring

## Optional System Tools Installation

### Debian/Ubuntu
```bash
sudo apt install pciutils util-linux smartmontools
```

### Fedora
```bash
sudo dnf install pciutils util-linux smartmontools
```

### Arch
```bash
sudo pacman -S pciutils util-linux smartmontools
```

## Troubleshooting

### Permission Denied
```bash
chmod +x SystemInfoTool
```

### Missing Dependencies
```bash
pip3 install -r requirements.txt
```

### Missing System Tools
Install the optional tools listed above for enhanced hardware detection.

## Version
1.0.0 - Initial release with enhanced hardware detection