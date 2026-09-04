#!/bin/bash
# Build script for System Info Tool on Linux

echo "=========================================="
echo "System Info Tool Linux Build Script"
echo "=========================================="
echo "Platform: $(uname -s)"
echo "Architecture: $(uname -m)"
echo "=========================================="

# Check Python version
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3 not found"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Install PyInstaller
echo "Installing PyInstaller..."
pip3 install pyinstaller
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install PyInstaller"
    exit 1
fi

# Build executable
echo "Building executable with PyInstaller..."
python3 -m PyInstaller --onefile --name=SystemInfoTool --add-data="collectors:collectors" --hidden-import=customtkinter --hidden-import=PIL main.py
if [ $? -ne 0 ]; then
    echo "ERROR: PyInstaller build failed"
    exit 1
fi

# Set executable permissions
chmod +x dist/SystemInfoTool
echo "Set executable permissions"

# Create portable flag
touch dist/portable.flag
echo "Created portable flag"

echo "=========================================="
echo "Build completed successfully!"
echo "Executable location: dist/SystemInfoTool"
echo "Portable build: dist/SystemInfoTool + dist/portable.flag"
echo "=========================================="