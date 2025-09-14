#!/bin/bash
# Mac-specific run script for Bulk Video Downloader

echo "🍎 Bulk Video Downloader - Mac Launcher"
echo "========================================"

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for macOS only"
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found, using system Python"
fi

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python3 -c "import PyQt6" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ PyQt6 not found. Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

# Run the application
echo "🚀 Starting Bulk Video Downloader..."
python3 src/main.py

echo "👋 Application closed"
