# Mac Packaging Guide for Bulk Video Downloader

This guide explains how to package your Bulk Video Downloader as a native Mac application (.app bundle) and create distribution packages.

## Prerequisites

- macOS 10.13 or later
- Python 3.8+ (preferably 3.9+)
- Xcode Command Line Tools (for code signing)
- All project dependencies installed

## Quick Start

### Method 1: Automated Build (Recommended)

```bash
# Make the build script executable
chmod +x build_mac.py

# Run the automated build
python build_mac.py
```

This will:
- Install all dependencies
- Build the Mac application bundle
- Create a DMG installer
- Test the application

### Method 2: Manual Build

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Build the application
pyinstaller --clean bulk_video_downloader.spec

# 3. Test the application
open dist/BulkVideoDownloader.app
```

## Detailed Steps

### 1. Environment Setup

```bash
# Ensure you're in the project directory
cd /path/to/bulk_video_downloader

# Activate virtual environment (if using one)
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt
```

### 2. Create Application Icon (Optional)

For a professional look, create an app icon:

```bash
# Create icon.icns file (512x512 recommended)
# You can use online converters or:
# 1. Create icon.png (512x512)
# 2. Create icon.iconset directory with different sizes
# 3. Run: iconutil -c icns -o icon.icns icon.iconset
```

### 3. Build the Application

```bash
# Using the automated script
python build_mac.py

# Or manually with PyInstaller
pyinstaller --clean bulk_video_downloader.spec
```

### 4. Test the Application

```bash
# Test launch
open dist/BulkVideoDownloader.app

# Or from command line
dist/BulkVideoDownloader.app/Contents/MacOS/BulkVideoDownloader
```

## Distribution Options

### Option 1: DMG Installer (Recommended)

The automated script creates a DMG with:
- Drag-and-drop installation
- Applications folder shortcut
- Professional appearance

```bash
# DMG will be created as: BulkVideoDownloader-Installer.dmg
```

### Option 2: ZIP Archive

```bash
# Create ZIP distribution
zip -r BulkVideoDownloader-Mac.zip dist/BulkVideoDownloader.app
```

### Option 3: App Store Distribution

For App Store distribution, you'll need:
- Apple Developer Account ($99/year)
- Code signing certificates
- App Store Connect setup

## Code Signing (Optional but Recommended)

### For Development Distribution

```bash
# Create a self-signed certificate
security create-keypair -a rsa -s 2048 -f /tmp/BulkVideoDownloader.key
security add-identity -c /tmp/BulkVideoDownloader.key -k login.keychain

# Sign the application
codesign --force --verify --verbose --sign "BulkVideoDownloader" dist/BulkVideoDownloader.app
```

### For Distribution Outside App Store

```bash
# You'll need a Developer ID certificate from Apple
codesign --force --verify --verbose --sign "Developer ID Application: Your Name" dist/BulkVideoDownloader.app

# Notarize the application (required for macOS 10.15+)
xcrun altool --notarize-app --primary-bundle-id "com.shafayatnabi.bulkvideodownloader" --username "your-email@example.com" --password "app-specific-password" --file BulkVideoDownloader-Installer.dmg
```

## Troubleshooting

### Common Issues

**1. "App is damaged and can't be opened"**
```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine dist/BulkVideoDownloader.app
```

**2. PyQt6 not found**
```bash
# Ensure PyQt6 is installed
pip install PyQt6

# Or try PySide6 as alternative
pip install PySide6
```

**3. Missing dependencies**
```bash
# Check what's missing
otool -L dist/BulkVideoDownloader.app/Contents/MacOS/BulkVideoDownloader

# Reinstall with specific versions
pip install --upgrade -r requirements.txt
```

**4. Large file size**
```bash
# Exclude unnecessary modules in spec file
# Add to excludes list in Analysis()
```

### Debug Mode

To debug issues, enable console output:

```python
# In bulk_video_downloader.spec, change:
console=True  # Instead of False
```

### Check Application Bundle

```bash
# Verify app structure
ls -la dist/BulkVideoDownloader.app/Contents/

# Check Info.plist
plutil -p dist/BulkVideoDownloader.app/Contents/Info.plist
```

## Advanced Configuration

### Custom Info.plist

Edit the `info_plist` section in `bulk_video_downloader.spec` to customize:
- App version
- Bundle identifier
- Minimum macOS version
- Permissions and capabilities

### Universal Binary (Apple Silicon + Intel)

```bash
# Build for both architectures
arch -x86_64 python build_mac.py  # Intel
arch -arm64 python build_mac.py   # Apple Silicon

# Or use universal2 Python
python3 -m pip install --upgrade pip
pip install --upgrade setuptools wheel
```

### Reducing App Size

1. **Exclude unnecessary modules** in spec file
2. **Use UPX compression** (already enabled)
3. **Remove debug symbols** (strip=True)
4. **Exclude test files and documentation**

## Distribution Checklist

- [ ] Application launches without errors
- [ ] All features work correctly
- [ ] Icon displays properly
- [ ] App appears in Applications folder
- [ ] No console errors in debug mode
- [ ] File size is reasonable (< 200MB)
- [ ] DMG opens and installs correctly
- [ ] App can be deleted cleanly

## File Structure After Build

```
dist/
└── BulkVideoDownloader.app/
    ├── Contents/
    │   ├── Info.plist
    │   ├── MacOS/
    │   │   └── BulkVideoDownloader
    │   ├── Resources/
    │   │   └── icon.icns
    │   └── _internal/
    │       ├── base_library.zip
    │       ├── lib/
    │       └── ...
    └── ...
```

## Next Steps

1. **Test thoroughly** on different Mac systems
2. **Create installer graphics** for professional appearance
3. **Set up automated builds** with GitHub Actions
4. **Consider App Store submission** for wider distribution
5. **Implement auto-updates** for future versions

## Resources

- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [Apple Code Signing Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [macOS App Distribution](https://developer.apple.com/distribute/)
- [DMG Creation Tools](https://github.com/sindresorhus/create-dmg)
