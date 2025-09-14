#!/usr/bin/env python3
"""
Cross-platform build script for creating distributions for all platforms
This script helps you build for multiple platforms using Docker or CI/CD
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def create_dockerfile():
    """Create Dockerfile for cross-platform builds"""
    dockerfile_content = """
# Multi-stage build for cross-platform distribution
FROM python:3.9-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    libssl-dev \\
    libffi-dev \\
    python3-dev \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Build stage for Windows (using wine)
FROM base as windows-build
RUN apt-get update && apt-get install -y wine && rm -rf /var/lib/apt/lists/*
RUN wine --version || true  # Initialize wine
RUN pyinstaller --clean bulk_video_downloader.spec

# Build stage for Linux
FROM base as linux-build
RUN pyinstaller --clean bulk_video_downloader.spec

# Build stage for macOS (requires macOS host or cross-compilation tools)
FROM base as macos-build
# Note: macOS builds typically require a macOS host
# This is a placeholder for CI/CD systems that support macOS
RUN echo "macOS build would go here"
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    print("✅ Created Dockerfile for cross-platform builds")

def create_github_workflow():
    """Create GitHub Actions workflow for automated builds"""
    workflow_content = """
name: Build Cross-Platform Executables

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build:
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            platform: linux
          - os: windows-latest
            platform: windows
          - os: macos-latest
            platform: macos

    runs-on: ${{ matrix.os }}

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Build executable
      run: |
        python build.py

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: BulkVideoDownloader-${{ matrix.platform }}
        path: release_${{ matrix.platform }}/

    - name: Create Release
      if: startsWith(github.ref, 'refs/tags/')
      uses: softprops/action-gh-release@v1
      with:
        files: release_${{ matrix.platform }}/*
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""
    
    os.makedirs('.github/workflows', exist_ok=True)
    with open('.github/workflows/build.yml', 'w') as f:
        f.write(workflow_content)
    print("✅ Created GitHub Actions workflow")

def create_manual_build_instructions():
    """Create manual build instructions for each platform"""
    instructions = """
# Manual Build Instructions

## Prerequisites
- Python 3.9+
- All dependencies from requirements.txt
- PyInstaller

## Building for Each Platform

### Windows
```bash
# Install dependencies
pip install -r requirements.txt

# Build executable
pyinstaller --clean bulk_video_downloader.spec

# The executable will be in dist/BulkVideoDownloader.exe
```

### Linux (Ubuntu/Debian)
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-dev build-essential

# Install Python dependencies
pip install -r requirements.txt

# Build executable
pyinstaller --clean bulk_video_downloader.spec

# The executable will be in dist/BulkVideoDownloader
```

### macOS
```bash
# Install dependencies
pip install -r requirements.txt

# Build executable
pyinstaller --clean bulk_video_downloader.spec

# The executable will be in dist/BulkVideoDownloader
```

## Testing the Executable
1. Navigate to the dist/ directory
2. Run the executable:
   - Windows: `BulkVideoDownloader.exe`
   - Linux/macOS: `./BulkVideoDownloader`

## Distribution
- Copy the entire dist/ directory to your target system
- Ensure the executable has proper permissions (Unix systems)
- Test on the target platform before distribution
"""
    
    with open('BUILD_INSTRUCTIONS.md', 'w') as f:
        f.write(instructions)
    print("✅ Created manual build instructions")

def main():
    """Create all necessary files for cross-platform builds"""
    print("🔧 Setting up cross-platform build environment...")
    
    # Create Docker setup
    create_dockerfile()
    
    # Create GitHub Actions workflow
    create_github_workflow()
    
    # Create manual instructions
    create_manual_build_instructions()
    
    print("\n🎉 Cross-platform build setup completed!")
    print("\n📋 Next steps:")
    print("1. Run 'python build.py' to build for your current platform")
    print("2. For automated builds, push to GitHub and create a release tag")
    print("3. For manual builds on other platforms, follow BUILD_INSTRUCTIONS.md")

if __name__ == "__main__":
    main()

