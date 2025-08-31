#!/usr/bin/env python3
"""
Simple runner script for the Bulk Video Downloader
"""

import subprocess
import sys
import os

def main():
    """Run the application with virtual environment activated"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the main application
    main_app = os.path.join(script_dir, "src", "main.py")
    
    # Path to the virtual environment
    venv_python = os.path.join(script_dir, "venv", "bin", "python")
    
    # Check if virtual environment exists
    if not os.path.exists(venv_python):
        print("Virtual environment not found. Please run:")
        print("python3 -m venv venv")
        print("source venv/bin/activate")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # Run the application
    try:
        subprocess.run([venv_python, main_app], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
