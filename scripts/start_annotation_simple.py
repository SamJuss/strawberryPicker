#!/usr/bin/env python3
"""
Simple script to start manual annotation immediately
No interactive prompts - just starts the web tool
"""

import subprocess
import sys
import webbrowser
import time
from pathlib import Path

def start_annotation():
    """Start the web labeling tool for manual annotation"""
    
    print("🎯 STARTING MANUAL ANNOTATION")
    print("=" * 60)
    print("Starting the web labeling tool...")
    print("=" * 60)
    
    # Check if the web labeling script exists
    script_path = Path("scripts/label_images_web.py")
    if not script_path.exists():
        print("❌ Web labeling script not found at scripts/label_images_web.py")
        print("🔄 Please ensure the labeling tool is available")
        return False
    
    print("✅ Web labeling script found")
    print("🚀 Starting the labeling server...")
    print("📡 Server will start on http://localhost:5000")
    
    try:
        # Start the web server
        print("⏳ Starting server (this may take a moment)...")
        process = subprocess.Popen([sys.executable, str(script_path)])
        
        # Wait for server to start
        time.sleep(4)
        
        # Open browser
        print("🌐 Opening browser automatically...")
        webbrowser.open('http://localhost:5000')
        
        print("\n✅ Web labeling tool started successfully!")
        print("🌐 Your browser should open to: http://localhost:5000")
        print("📋 Follow the instructions on the web interface")
        print("⏰ Take your time - quality over speed!")
        print("🎯 Goal: Perfect bounding boxes for robotic picking")
        
        print("\n" + "=" * 60)
        print("💡 TIPS FOR SUCCESS:")
        print("• Draw tight boxes around each strawberry")
        print("• Ensure complete coverage of visible berries")
        print("• Minimize background pixels in boxes")
        print("• Each strawberry gets its own box")
        print("• Review each image before moving to next")
        print("=" * 60)
        
        print("\n📝 When you're done labeling all images:")
        print("1. Close the browser tab")
        print("2. Press Ctrl+C here to stop the server")
        print("3. Your labels will be saved automatically")
        
        # Keep the script running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping annotation server...")
            process.terminate()
            print("✅ Server stopped. Your labels have been saved!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error starting annotation tool: {e}")
        print("🔄 Please try manual setup:")
        print("   python3 scripts/label_images_web.py")
        print("   Then open browser to: http://localhost:5000")
        return False

def show_quick_tips():
    """Show quick tips for annotation"""
    
    print("\n🎯 QUICK ANNOTATION TIPS:")
    print("-" * 40)
    print("✅ DO:")
    print("  • Draw tight boxes around strawberries")
    print("  • Include entire visible berry")
    print("  • Make separate boxes for each berry")
    print("  • Take your time for quality")
    
    print("\n❌ DON'T:")
    print("  • Draw loose boxes with lots of background")
    print("  • Cut off parts of strawberries")
    print("  • Put multiple berries in one box")
    print("  • Rush through the process")

def main():
    """Main function to start annotation"""
    
    print("🎯 MANUAL ANNOTATION - QUICK START")
    print("=" * 60)
    print("This will start the web labeling tool immediately")
    print("=" * 60)
    
    # Show quick tips
    show_quick_tips()
    
    # Start annotation
    if start_annotation():
        print("\n🎉 Annotation tool is running!")
        print("📝 Start labeling your images now!")
    else:
        print("\n❌ Failed to start annotation tool")
        print("📋 Please check the setup and try manual start")

if __name__ == '__main__':
    main()