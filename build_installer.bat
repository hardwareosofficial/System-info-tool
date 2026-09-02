@echo off
REM Build script for System Info Tool Windows Installer
REM This script builds the executable and creates a Windows installer using Inno Setup

echo ==========================================
echo System Info Tool Installer Build Script
echo ==========================================
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

REM Step 2: Check if Inno Setup is available
echo Step 2: Checking for Inno Setup...
where ISCC.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Inno Setup found
    echo.
    
    REM Step 3: Build the installer
    echo Step 3: Building Windows installer with Inno Setup...
    ISCC.exe SystemInfoTool.iss
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Inno Setup build failed
        pause
        exit /b 1
    )
    echo Windows installer built successfully
    echo.
    
    echo ==========================================
    echo Build completed successfully!
    echo Installer location: Output\SystemInfoTool-Setup.exe
    echo Portable build: dist\SystemInfoTool.exe + dist\portable.flag
    echo ==========================================
) else (
    echo Inno Setup not found
    echo Please install Inno Setup from: https://jrsoftware.org/isinfo.php
    echo.
    echo Alternatively, use the Qt Installer Framework for cross-platform installers
    echo See BUILD_INSTRUCTIONS.md for details
    echo.
    echo ==========================================
    echo Executable build completed successfully!
    echo Executable location: dist\SystemInfoTool.exe
    echo Portable build: dist\SystemInfoTool.exe + dist\portable.flag
    echo ==========================================
)

pause