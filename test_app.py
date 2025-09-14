#!/usr/bin/env python3
"""
Test script to verify the Mac app is working correctly
"""

import subprocess
import time
import os
import signal

def test_app_launch():
    """Test if the app launches without crashing"""
    print("🧪 Testing Mac app launch...")
    
    app_path = "dist/BulkVideoDownloader.app/Contents/MacOS/BulkVideoDownloader"
    
    if not os.path.exists(app_path):
        print("❌ App not found at:", app_path)
        return False
    
    try:
        # Launch the app
        process = subprocess.Popen([app_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # Wait a bit for the app to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ App launched successfully and is running")
            
            # Terminate the app
            process.terminate()
            process.wait(timeout=5)
            print("✅ App terminated cleanly")
            return True
        else:
            # Process exited, check for errors
            stdout, stderr = process.communicate()
            print("❌ App crashed on startup")
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error testing app: {e}")
        return False

def test_app_structure():
    """Test if the app bundle has the correct structure"""
    print("🔍 Testing app bundle structure...")
    
    app_bundle = "dist/BulkVideoDownloader.app"
    required_files = [
        "Contents/Info.plist",
        "Contents/MacOS/BulkVideoDownloader",
        "Contents/Resources",
    ]
    
    for file_path in required_files:
        full_path = os.path.join(app_bundle, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Bulk Video Downloader Mac App")
    print("=" * 50)
    
    # Test app structure
    if not test_app_structure():
        print("\n❌ App structure test failed")
        return False
    
    # Test app launch
    if not test_app_launch():
        print("\n❌ App launch test failed")
        return False
    
    print("\n🎉 All tests passed! The app is working correctly.")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
