@echo off
REM Run this ON WINDOWS, from inside the sysinfo_app folder, to produce
REM a real SystemInfoTool.exe. PyInstaller must run on the target OS —
REM it bundles that OS's own Python + DLLs, it doesn't cross-compile.
REM
REM Usage:
REM   1. Install Python 3.10+ from python.org if you don't have it
REM      (tick "Add python.exe to PATH" during install).
REM   2. Double-click this file, or run it from a Command Prompt.

echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo.
echo Building SystemInfoTool.exe ...
python -m PyInstaller --onefile --windowed --name SystemInfoTool main.py

echo.
echo Marking the build as portable (no install, no host-machine files)...
type nul > dist\portable.flag

echo.
echo Done. Your executable is at: dist\SystemInfoTool.exe
echo Ship dist\SystemInfoTool.exe together with dist\portable.flag
echo (same folder, e.g. on a USB stick) for a fully portable build.

echo.
echo Looking for Inno Setup's compiler (ISCC.exe) to also build an installer...
where ISCC >nul 2>nul
if %errorlevel%==0 (
    echo Found ISCC — compiling SystemInfoTool-Setup.exe ...
    ISCC SystemInfoTool.iss
    echo Installer built: Output\SystemInfoTool-Setup.exe
) else (
    echo ISCC not found on PATH — skipping installer build.
    echo Install Inno Setup from https://jrsoftware.org/isinfo.php, then
    echo either re-run this script or open SystemInfoTool.iss in the
    echo Inno Setup Compiler and press Build.
)
pause
