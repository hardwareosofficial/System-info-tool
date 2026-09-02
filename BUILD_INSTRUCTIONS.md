# Build Instructions

## Prerequisites

### Common Requirements
- Python 3.8+
- pip package manager

### Platform-Specific Requirements

#### Windows
- Python 3.8+
- pywin32 (via pip)
- wmi (via pip)
- PyInstaller (via pip)
- Inno Setup (optional, for Windows installer)

#### Linux
- Python 3.8+
- psutil (via pip)
- customtkinter (via pip)
- PyInstaller (via pip)
- Qt Installer Framework (optional, for Linux installer)

#### macOS
- Python 3.8+
- psutil (via pip)
- customtkinter (via pip)
- PyInstaller (via pip)
- Qt Installer Framework (optional, for macOS installer)

## Building with PyInstaller

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### Step 2: Build Executable

#### Using the build script (recommended):
```bash
python build.py
```

#### Manual PyInstaller command:

**Windows:**
```bash
python -m PyInstaller --onefile --windowed --name=SystemInfoTool --add-data="collectors;collectors" --hidden-import=customtkinter --hidden-import=PIL main.py
```

**Linux:**
```bash
python -m PyInstaller --onefile --name=SystemInfoTool --add-data="collectors:collectors" --hidden-import=customtkinter --hidden-import=PIL main.py
```

**macOS:**
```bash
python -m PyInstaller --onefile --windowed --name=SystemInfoTool --icon=icon.icns --add-data="collectors:collectors" --hidden-import=customtkinter --hidden-import=PIL --osx-bundle-identifier=com.systeminfotool.app main.py
```

### Step 3: Output

The built executable will be located in the `dist/` directory:
- Windows: `dist/SystemInfoTool.exe`
- Linux: `dist/SystemInfoTool`
- macOS: `dist/SystemInfoTool` (or `dist/SystemInfoTool.app` if bundled)

The build script also automatically creates a `portable.flag` file for portable mode.

## Building Windows Installer with Inno Setup

### Step 1: Install Inno Setup

Download and install Inno Setup from: https://jrsoftware.org/isinfo.php

### Step 2: Build Installer

#### Using the build script (recommended):
```bash
build_installer.bat
```

#### Manual build:
1. First build the executable: `python build.py`
2. Run Inno Setup compiler: `ISCC.exe SystemInfoTool.iss`

### Step 3: Output

The Windows installer will be located in the `Output/` directory:
- `Output/SystemInfoTool-Setup.exe`

## Building with Qt Installer Framework

### Step 1: Install Qt Installer Framework

Download and install Qt Installer Framework from: https://github.com/Qt-Project/Qt-Installer-Framework

Add the Qt Installer Framework `bin` directory to your system PATH.

### Step 2: Build Installer

#### Using the build script (recommended):
```bash
build_qt_installer.bat
```

#### Manual build:
1. First build the executable: `python build.py`
2. Copy executable to Qt Installer Framework data directory:
   ```bash
   copy dist\SystemInfoTool.exe qt_installer_config\packages\com.systeminfotool.app\data\
   copy dist\portable.flag qt_installer_config\packages\com.systeminfotool.app\data\
   ```
3. Build the installer:
   ```bash
   binarycreator.exe -c qt_installer_config\config.xml -p qt_installer_config\packages Output\SystemInfoTool-QtInstaller
   ```

### Step 3: Output

The Qt Installer Framework installer will be located in the `Output/` directory:
- `Output/SystemInfoTool-QtInstaller.exe`

## Building Windows Installer with Inno Setup

### Step 1: Install Inno Setup

Download and install Inno Setup from: https://jrsoftware.org/isinfo.php

### Step 2: Build Installer

#### Using the build script (recommended):
```bash
build_installer.bat
```

#### Manual build:
1. First build the executable: `python build.py`
2. Run Inno Setup compiler: `ISCC.exe SystemInfoTool.iss`

### Step 3: Output

The Windows installer will be located in the `Output/` directory:
- `Output/SystemInfoTool-Setup.exe`

## Building with Qt Installer Framework

### Step 1: Install Qt Installer Framework

Download and install Qt Installer Framework from: https://github.com/Qt-Project/Qt-Installer-Framework

Add the Qt Installer Framework `bin` directory to your system PATH.

### Step 2: Build Installer

#### Using the build script (recommended):
```bash
build_qt_installer.bat
```

#### Manual build:
1. First build the executable: `python build.py`
2. Copy executable to Qt Installer Framework data directory:
   ```bash
   copy dist\SystemInfoTool.exe qt_installer_config\packages\com.systeminfotool.app\data\
   copy dist\portable.flag qt_installer_config\packages\com.systeminfotool.app\data\
   ```
3. Build the installer:
   ```bash
   binarycreator.exe -c qt_installer_config\config.xml -p qt_installer_config\packages Output\SystemInfoTool-QtInstaller
   ```

### Step 3: Output

The Qt Installer Framework installer will be located in the `Output/` directory:
- `Output/SystemInfoTool-QtInstaller.exe`

### Platform-Specific Notes

**Windows:**
- Use Inno Setup as an alternative to Qt Installer Framework
- Run the provided `build_installer.bat` script

**Linux:**
- Ensure proper permissions are set on the executable
- Consider creating .desktop file for desktop integration

**macOS:**
- Code signing may be required for distribution
- Notarization needed for macOS 11+ outside of App Store

## Cross-Platform Testing

To ensure the application works on all platforms:

1. **Test on each target platform:**
   - Windows 10/11
   - Major Linux distributions (Ubuntu, Fedora, Arch)
   - macOS 10.15+

2. **Verify platform-specific features:**
   - Windows: WMI data collection, detailed drivers
   - Linux: /proc and /sys data, lspci support
   - macOS: system_profiler data, kextstat support

3. **Test fallback behavior:**
   - Ensure graceful degradation when platform-specific tools are missing
   - Verify error handling for missing permissions

## Portable Mode

To create a portable build:

1. Build the executable using PyInstaller
2. The build script automatically creates a `portable.flag` file
3. Ship the executable + portable.flag together
4. For manual portable mode, simply create an empty `portable.flag` file next to the executable

## Troubleshooting

### Common Issues

**ImportError on non-Windows platforms:**
- Ensure Windows-specific imports are properly isolated
- Check that platform detection is working correctly

**Missing dependencies:**
- Run `pip install -r requirements.txt` on each platform
- Verify platform-specific dependencies are marked correctly in requirements.txt

**PyInstaller build failures:**
- Ensure all data files are included with --add-data
- Check that hidden imports are specified for dynamic imports
- Verify icon files exist for the target platform

**Installer creation failures:**
- Ensure Qt Installer Framework is properly installed
- Check that package.xml structure is correct
- Verify executable is in the correct data directory

## Performance Optimization

The application includes several performance optimizations:

1. **Data collection limits:**
   - Drivers: Limited to 50 items
   - PCI devices: Limited to 20 items
   - USB controllers: Limited to 15 items

2. **UI rendering limits:**
   - Maximum 200 rows per tab
   - Lazy tab rendering on demand

3. **Background data collection:**
   - Data collection runs in separate thread
   - UI remains responsive during refresh

These optimizations ensure the application runs smoothly even on systems with extensive hardware configurations.