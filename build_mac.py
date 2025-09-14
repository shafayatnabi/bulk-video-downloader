#!/usr/bin/env python3
"""
Mac-specific build script for Bulk Video Downloader
Creates a proper Mac application bundle and DMG installer
"""

import os
import sys
import subprocess
import shutil
import platform
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

def check_mac_environment():
    """Check if we're running on macOS"""
    if platform.system() != "Darwin":
        print("❌ This script is designed for macOS only")
        return False
    
    print(f"✅ Running on macOS {platform.mac_ver()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing/updating dependencies...")
    
    # Install PyInstaller if not present
    try:
        import PyInstaller
        print("✅ PyInstaller is already installed")
    except ImportError:
        if not run_command("pip install pyinstaller", "Installing PyInstaller"):
            return False
    
    # Install other dependencies
    if not run_command("pip install -r requirements.txt", "Installing project dependencies"):
        return False
    
    return True

def create_app_icon():
    """Create a simple app icon if none exists"""
    icon_path = "icon.icns"
    if not os.path.exists(icon_path):
        print("📝 Creating a simple app icon...")
        # Create a simple 512x512 icon using Python (basic approach)
        try:
            from PIL import Image, ImageDraw
            import io
            
            # Create a simple icon
            img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw a simple video camera icon
            draw.rectangle([50, 50, 462, 462], fill=(52, 152, 219), outline=(41, 128, 185), width=8)
            draw.rectangle([100, 100, 412, 412], fill=(236, 240, 241))
            draw.polygon([(200, 150), (200, 362), (350, 256)], fill=(52, 152, 219))
            
            # Save as PNG first
            img.save("icon.png", "PNG")
            print("✅ Created icon.png")
            
            # Convert to ICNS (requires iconutil on macOS)
            if run_command("iconutil -c icns -o icon.icns icon.iconset", "Converting to ICNS"):
                print("✅ Created icon.icns")
            else:
                print("⚠️  Could not create ICNS, will use PNG")
                icon_path = "icon.png"
                
        except ImportError:
            print("⚠️  PIL not available, skipping icon creation")
            icon_path = None
        except Exception as e:
            print(f"⚠️  Could not create icon: {e}")
            icon_path = None
    
    return icon_path

def build_mac_app():
    """Build the Mac application using PyInstaller"""
    print("🔨 Building Mac application...")
    
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 Cleaned {dir_name}/")
    
    # Get icon path
    icon_path = create_app_icon()
    
    # Build command for Mac
    cmd = "pyinstaller --clean bulk_video_downloader.spec"
    if icon_path:
        cmd += f" --icon={icon_path}"
    
    if not run_command(cmd, "Building Mac application"):
        return False
    
    # Check if the app was created
    app_path = "dist/BulkVideoDownloader.app"
    if not os.path.exists(app_path):
        print("❌ Application bundle not found")
        return False
    
    print(f"✅ Mac application created: {app_path}")
    return True

def create_dmg_installer():
    """Create a DMG installer for easy distribution"""
    print("💿 Creating DMG installer...")
    
    app_path = "dist/BulkVideoDownloader.app"
    dmg_name = "BulkVideoDownloader-Installer"
    
    if not os.path.exists(app_path):
        print("❌ Application not found, cannot create DMG")
        return False
    
    # Create a temporary directory for DMG contents
    dmg_dir = "dmg_contents"
    if os.path.exists(dmg_dir):
        shutil.rmtree(dmg_dir)
    os.makedirs(dmg_dir)
    
    # Copy the app to DMG directory
    shutil.copytree(app_path, f"{dmg_dir}/BulkVideoDownloader.app")
    
    # Create a symbolic link to Applications folder
    os.symlink("/Applications", f"{dmg_dir}/Applications")
    
    # Copy README and other files
    for file in ['README.md', 'requirements.txt']:
        if os.path.exists(file):
            shutil.copy2(file, dmg_dir)
    
    # Create DMG using hdiutil
    dmg_cmd = f"hdiutil create -volname 'Bulk Video Downloader' -srcfolder {dmg_dir} -ov -format UDZO {dmg_name}.dmg"
    
    if run_command(dmg_cmd, "Creating DMG installer"):
        print(f"✅ DMG installer created: {dmg_name}.dmg")
        
        # Clean up temporary directory
        shutil.rmtree(dmg_dir)
        return True
    else:
        print("❌ Failed to create DMG installer")
        return False

def create_zip_distribution():
    """Create a ZIP distribution as fallback"""
    print("📦 Creating ZIP distribution...")
    
    app_path = "dist/BulkVideoDownloader.app"
    zip_name = "BulkVideoDownloader-Mac.zip"
    
    if not os.path.exists(app_path):
        print("❌ Application not found, cannot create ZIP")
        return False
    
    # Create ZIP using Python
    import zipfile
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(app_path):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, "dist")
                zipf.write(file_path, arc_path)
    
    print(f"✅ ZIP distribution created: {zip_name}")
    return True

def test_application():
    """Test the built application"""
    print("🧪 Testing the application...")
    
    app_path = "dist/BulkVideoDownloader.app"
    if not os.path.exists(app_path):
        print("❌ Application not found for testing")
        return False
    
    # Try to run the application
    test_cmd = f"open {app_path}"
    if run_command(test_cmd, "Testing application launch"):
        print("✅ Application launched successfully")
        return True
    else:
        print("⚠️  Could not test application launch")
        return False

def main():
    """Main build process for Mac"""
    print("🍎 Starting Mac build process for Bulk Video Downloader...")
    
    # Check environment
    if not check_mac_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Build the application
    if not build_mac_app():
        print("❌ Failed to build Mac application")
        sys.exit(1)
    
    # Test the application
    test_application()
    
    # Create distributions
    print("\n📦 Creating distribution packages...")
    
    # Try to create DMG first
    if not create_dmg_installer():
        print("⚠️  DMG creation failed, creating ZIP instead")
        create_zip_distribution()
    
    print("\n🎉 Mac build completed successfully!")
    print("\n📋 Distribution files created:")
    
    if os.path.exists("BulkVideoDownloader-Installer.dmg"):
        print("  • BulkVideoDownloader-Installer.dmg (Recommended)")
    
    if os.path.exists("BulkVideoDownloader-Mac.zip"):
        print("  • BulkVideoDownloader-Mac.zip (Alternative)")
    
    print("\n📱 To install:")
    print("  1. Double-click the DMG file")
    print("  2. Drag BulkVideoDownloader.app to Applications folder")
    print("  3. Launch from Applications or Launchpad")
    
    print("\n🔧 For distribution:")
    print("  • DMG: Professional installer with drag-and-drop")
    print("  • ZIP: Simple archive, extract and run")

if __name__ == "__main__":
    main()
