System Info Tool - macOS Release
=================================

## Building the macOS Version

Since macOS builds require a macOS environment, you need to build the executable on a Mac.

### Prerequisites
- macOS 10.15 (Catalina) or later
- Python 3.8 or higher
- pip package manager
- Xcode Command Line Tools (for some dependencies)

### Build Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/hardwareosofficial/System-info-tool.git
   cd System-info-tool
   ```

2. Run the build script:
   ```bash
   chmod +x build_macos.sh
   ./build_macos.sh
   ```

3. Or build manually:
   ```bash
   pip3 install -r requirements.txt
   pip3 install pyinstaller
   python3 -m PyInstaller --onefile --windowed --name=SystemInfoTool --add-data="collectors:collectors" --hidden-import=customtkinter --hidden-import=PIL --osx-bundle-identifier=com.systeminfotool.app main.py
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

## macOS-Specific Features
- system_profiler integration for hardware info
- Apple Silicon (M1/M2/M3) support
- kextstat for driver information
- Battery health and cycle count
- Firmware version information
- Hardware UUID detection

## Code Signing (Optional)

For distribution outside of App Store:

```bash
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/SystemInfoTool
```

## Notarization (Optional for macOS 11+)

For distribution on macOS 11+ outside of App Store, you may need to notarize the application.

## Troubleshooting

### Permission Denied
```bash
chmod +x SystemInfoTool
```

### Gatekeeper Blocking
If macOS blocks the app:
1. Right-click the app and select "Open"
2. Or disable Gatekeeper temporarily: `sudo spctl --master-disable`

### Missing Dependencies
```bash
pip3 install -r requirements.txt
```

## Version
1.0.0 - Initial release with enhanced hardware detection