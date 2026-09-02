@echo off
REM Build script for System Info Tool using Qt Installer Framework
REM This script requires Qt Installer Framework to be installed

echo ==========================================
echo Qt Installer Framework Build Script
echo ==========================================
echo.

REM Check if Qt Installer Framework is available
where binarycreator.exe >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Qt Installer Framework not found
    echo Please install Qt Installer Framework from: https://github.com/Qt-Project/Qt-Installer-Framework
    echo After installation, add the bin directory to your PATH
    pause
    exit /b 1
)

echo Qt Installer Framework found
echo.

REM Step 1: Build the executable with PyInstaller
echo Step 1: Building executable with PyInstaller...
python build.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)
echo PyInstaller build completed successfully
echo.

REM Step 2: Copy executable to Qt Installer Framework data directory
echo Step 2: Copying executable to Qt Installer Framework data directory...
copy dist\SystemInfoTool.exe qt_installer_config\packages\com.systeminfotool.app\data\
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to copy executable
    pause
    exit /b 1
)
copy dist\portable.flag qt_installer_config\packages\com.systeminfotool.app\data\
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to copy portable flag
    pause
    exit /b 1
)
echo Files copied successfully
echo.

REM Step 3: Build the installer
echo Step 3: Building installer with Qt Installer Framework...
if not exist Output mkdir Output
binarycreator.exe -c qt_installer_config\config.xml -p qt_installer_config\packages Output\SystemInfoTool-QtInstaller
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Qt Installer Framework build failed
    pause
    exit /b 1
)
echo Qt Installer Framework build completed successfully
echo.

echo ==========================================
echo Build completed successfully!
echo Installer location: Output\SystemInfoTool-QtInstaller.exe
echo ==========================================
pause