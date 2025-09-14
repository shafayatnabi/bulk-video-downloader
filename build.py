#!/usr/bin/env python3
"""
Build script for creating cross-platform distributions
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller is already installed")
        return True
    except ImportError:
        print("📦 Installing PyInstaller...")
        return run_command("pip install pyinstaller", "PyInstaller installation")

def build_executable():
    """Build the executable using PyInstaller"""
    system = platform.system().lower()
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Build command based on platform
    if system == "windows":
        cmd = "pyinstaller --clean bulk_video_downloader.spec"
    else:
        cmd = "pyinstaller --clean bulk_video_downloader.spec"
    
    return run_command(cmd, f"Building executable for {system}")

def create_release_package():
    """Create a release package with necessary files"""
    system = platform.system().lower()
    release_dir = f"release_{system}"
    
    # Create release directory
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    # Copy executable
    exe_name = "BulkVideoDownloader.exe" if system == "windows" else "BulkVideoDownloader"
    exe_path = f"dist/{exe_name}"
    
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, release_dir)
        print(f"✅ Copied executable to {release_dir}/")
    else:
        print(f"❌ Executable not found at {exe_path}")
        return False
    
    # Copy additional files
    files_to_copy = ['README.md', 'requirements.txt']
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, release_dir)
            print(f"✅ Copied {file} to {release_dir}/")
    
    # Create a simple run script for Unix systems
    if system != "windows":
        run_script = f"{release_dir}/run.sh"
        with open(run_script, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write(f"./{exe_name}\n")
        os.chmod(run_script, 0o755)
        print(f"✅ Created run script: {run_script}")
    
    print(f"\n🎉 Release package created in: {release_dir}/")
    return True

def main():
    """Main build process"""
    print("🚀 Starting cross-platform build process...")
    
    # Check if we're in the right directory
    if not os.path.exists('src/main.py'):
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Install PyInstaller
    if not install_pyinstaller():
        sys.exit(1)
    
    # Build executable
    if not build_executable():
        sys.exit(1)
    
    # Create release package
    if not create_release_package():
        sys.exit(1)
    
    print("\n🎉 Build completed successfully!")
    print(f"📦 Your executable is ready in the release_{platform.system().lower()}/ directory")

if __name__ == "__main__":
    main()

