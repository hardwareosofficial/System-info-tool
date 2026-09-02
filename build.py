"""
Build script for System Info Tool using PyInstaller.
Supports cross-platform building for Windows, Linux, and macOS.
"""
import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        print(f"PyInstaller found: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        # Try to import again after installation
        try:
            import PyInstaller
            print(f"PyInstaller installed successfully: {PyInstaller.__version__}")
            return True
        except ImportError:
            print("Failed to import PyInstaller after installation")
            return False


def build_executable():
    """Build the executable using PyInstaller."""
    system = platform.system()
    
    # Base PyInstaller arguments using python -m to avoid PATH issues
    pyinstaller_args = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=SystemInfoTool",
        "main.py"
    ]
    
    # Add icon only if file exists
    if system == "Windows" and Path("icon.ico").exists():
        pyinstaller_args.append("--icon=icon.ico")
    elif system == "Darwin" and Path("icon.icns").exists():
        pyinstaller_args.append("--icon=icon.icns")
    
    # Platform-specific arguments
    if system == "Windows":
        pyinstaller_args.extend([
            "--add-data=collectors;collectors",
            "--hidden-import=customtkinter",
            "--hidden-import=PIL",
        ])
    elif system == "Darwin":  # macOS
        pyinstaller_args.extend([
            "--add-data=collectors:collectors",
            "--hidden-import=customtkinter",
            "--hidden-import=PIL",
            "--osx-bundle-identifier=com.systeminfotool.app",
        ])
    else:  # Linux
        pyinstaller_args.extend([
            "--add-data=collectors:collectors",
            "--hidden-import=customtkinter",
            "--hidden-import=PIL",
        ])
    
    print(f"Building for {system}...")
    print(f"Command: {' '.join(pyinstaller_args)}")
    
    try:
        subprocess.check_call(pyinstaller_args)
        print("Build successful!")
        
        # Set executable permissions on Unix-like systems
        if system != "Windows":
            exe_path = Path("dist/SystemInfoTool")
            if exe_path.exists():
                os.chmod(exe_path, 0o755)
                print(f"Set executable permissions on {exe_path}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False


def create_portable_flag():
    """Create portable.flag file for portable mode."""
    dist_dir = Path("dist")
    if dist_dir.exists():
        portable_flag = dist_dir / "portable.flag"
        portable_flag.touch()
        print(f"Created portable flag: {portable_flag}")


def main():
    """Main build function."""
    print("=" * 50)
    print("System Info Tool Build Script")
    print("=" * 50)
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")
    print(f"Architecture: {platform.machine()}")
    print("=" * 50)
    
    # Check for PyInstaller
    if not check_pyinstaller():
        print("Failed to install PyInstaller")
        return 1
    
    # Build the executable
    if not build_executable():
        print("Build failed")
        return 1
    
    # Create portable flag
    create_portable_flag()
    
    print("=" * 50)
    print("Build completed successfully!")
    print(f"Executable location: dist/SystemInfoTool")
    print("=" * 50)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())