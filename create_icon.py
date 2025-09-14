#!/usr/bin/env python3
"""
Simple icon creation script for Bulk Video Downloader
Creates a basic app icon in various formats
"""

import os
import sys
from pathlib import Path

def create_simple_icon():
    """Create a simple icon using basic Python libraries"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        print("✅ PIL available, creating icon with PIL")
        return create_pil_icon()
    except ImportError:
        print("⚠️  PIL not available, creating basic icon")
        return create_basic_icon()

def create_pil_icon():
    """Create icon using PIL"""
    try:
        # Create a 512x512 image
        size = 512
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Background circle
        margin = 20
        draw.ellipse([margin, margin, size-margin, size-margin], 
                    fill=(52, 152, 219), outline=(41, 128, 185), width=8)
        
        # Inner circle
        inner_margin = 80
        draw.ellipse([inner_margin, inner_margin, size-inner_margin, size-inner_margin], 
                    fill=(236, 240, 241), outline=(189, 195, 199), width=4)
        
        # Video camera icon
        # Camera body
        body_x = size // 2 - 60
        body_y = size // 2 - 40
        body_width = 120
        body_height = 80
        draw.rounded_rectangle([body_x, body_y, body_x + body_width, body_y + body_height], 
                             radius=10, fill=(52, 152, 219))
        
        # Lens
        lens_center_x = size // 2
        lens_center_y = size // 2 - 10
        lens_radius = 30
        draw.ellipse([lens_center_x - lens_radius, lens_center_y - lens_radius,
                     lens_center_x + lens_radius, lens_center_y + lens_radius], 
                    fill=(236, 240, 241), outline=(189, 195, 199), width=3)
        
        # Play button triangle
        triangle_size = 20
        triangle_x = lens_center_x - 5
        triangle_y = lens_center_y - triangle_size // 2
        draw.polygon([
            (triangle_x, triangle_y),
            (triangle_x, triangle_y + triangle_size),
            (triangle_x + triangle_size, triangle_y + triangle_size // 2)
        ], fill=(52, 152, 219))
        
        # Save as PNG
        img.save("icon.png", "PNG")
        print("✅ Created icon.png")
        
        # Create iconset for ICNS
        create_iconset()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating PIL icon: {e}")
        return False

def create_iconset():
    """Create iconset directory for ICNS conversion"""
    try:
        from PIL import Image
        
        # Create iconset directory
        iconset_dir = Path("icon.iconset")
        iconset_dir.mkdir(exist_ok=True)
        
        # Required sizes for macOS
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        
        # Load the original image
        original = Image.open("icon.png")
        
        for size in sizes:
            # Resize image
            resized = original.resize((size, size), Image.Resampling.LANCZOS)
            
            # Save with appropriate name
            if size == 16:
                resized.save(iconset_dir / "icon_16x16.png")
            elif size == 32:
                resized.save(iconset_dir / "icon_16x16@2x.png")
                resized.save(iconset_dir / "icon_32x32.png")
            elif size == 64:
                resized.save(iconset_dir / "icon_32x32@2x.png")
                resized.save(iconset_dir / "icon_64x64.png")
            elif size == 128:
                resized.save(iconset_dir / "icon_64x64@2x.png")
                resized.save(iconset_dir / "icon_128x128.png")
            elif size == 256:
                resized.save(iconset_dir / "icon_128x128@2x.png")
                resized.save(iconset_dir / "icon_256x256.png")
            elif size == 512:
                resized.save(iconset_dir / "icon_256x256@2x.png")
                resized.save(iconset_dir / "icon_512x512.png")
            elif size == 1024:
                resized.save(iconset_dir / "icon_512x512@2x.png")
        
        print("✅ Created icon.iconset directory")
        
        # Convert to ICNS
        import subprocess
        result = subprocess.run([
            "iconutil", "-c", "icns", "-o", "icon.icns", "icon.iconset"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Created icon.icns")
            # Clean up iconset directory
            import shutil
            shutil.rmtree(iconset_dir)
            return True
        else:
            print(f"⚠️  Could not create ICNS: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating iconset: {e}")
        return False

def create_basic_icon():
    """Create a basic icon without PIL"""
    print("📝 Creating basic icon files...")
    
    # Create a simple SVG icon
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <circle cx="256" cy="256" r="240" fill="#3498db" stroke="#2980b9" stroke-width="8"/>
  <circle cx="256" cy="256" r="180" fill="#ecf0f1" stroke="#bdc3c7" stroke-width="4"/>
  <rect x="196" y="216" width="120" height="80" rx="10" fill="#3498db"/>
  <circle cx="256" cy="246" r="30" fill="#ecf0f1" stroke="#bdc3c7" stroke-width="3"/>
  <polygon points="241,231 241,261 271,246" fill="#3498db"/>
</svg>'''
    
    with open("icon.svg", "w") as f:
        f.write(svg_content)
    
    print("✅ Created icon.svg")
    print("💡 To convert to PNG/ICNS, use online converters or install PIL:")
    print("   pip install Pillow")
    
    return True

def main():
    """Main icon creation process"""
    print("🎨 Creating app icon for Bulk Video Downloader...")
    
    if create_simple_icon():
        print("\n✅ Icon creation completed!")
        print("\n📁 Files created:")
        
        if os.path.exists("icon.png"):
            print("  • icon.png (512x512)")
        if os.path.exists("icon.icns"):
            print("  • icon.icns (Mac app icon)")
        if os.path.exists("icon.svg"):
            print("  • icon.svg (Vector format)")
        
        print("\n🔧 Next steps:")
        print("  1. Run: python build_mac.py")
        print("  2. The icon will be automatically included in the app bundle")
        
    else:
        print("❌ Icon creation failed")
        print("💡 You can still build the app without an icon")

if __name__ == "__main__":
    main()
