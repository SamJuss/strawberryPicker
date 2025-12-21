#!/usr/bin/env python3
"""
Quick start script for manual annotation of Kaggle dataset
Walks you through the process step by step
"""

import os
import sys
from pathlib import Path
import subprocess
import webbrowser

def check_dataset_ready():
    """Check if the reduced dataset is ready for annotation"""
    
    dataset_path = Path("model/datasets/manual_labeled")
    
    print("🔍 Checking if dataset is ready for annotation...")
    
    # Check if dataset exists
    if not dataset_path.exists():
        print("❌ Dataset not found. Please run the reduction script first.")
        return False
    
    # Count images in each split
    total_images = 0
    for split in ['train', 'val', 'test']:
        split_path = dataset_path / split / 'images'
        if split_path.exists():
            images = list(split_path.glob("*.jpg")) + list(split_path.glob("*.png"))
            total_images += len(images)
            print(f"  📸 {split}: {len(images)} images")
    
    if total_images == 0:
        print("❌ No images found in dataset")
        return False
    
    print(f"✅ Found {total_images} images ready for annotation")
    return True

def show_annotation_options():
    """Show available annotation tools and options"""
    
    print("\n🛠️ Available Annotation Tools:")
    print("-" * 50)
    
    print("1. 🌐 Web Labeling Tool (Recommended - Same as Homemade Dataset)")
    print("   - Same interface you used before")
    print("   - Familiar and easy to use")
    print("   - Real-time preview")
    
    print("\n2. 🖼️ LabelImg (Alternative)")
    print("   - Popular open-source tool")
    print("   - Desktop application")
    print("   - More features and options")
    
    print("\n3. 🌐 CVAT (Advanced)")
    print("   - Web-based professional tool")
    print("   - Advanced features")
    print("   - Good for large projects")

def start_web_labeling_tool():
    """Start the web labeling tool"""
    
    print("\n🌐 Starting Web Labeling Tool...")
    print("=" * 60)
    
    # Check if the web labeling script exists
    script_path = Path("scripts/label_images_web.py")
    if not script_path.exists():
        print("❌ Web labeling script not found")
        return False
    
    print("✅ Web labeling script found")
    print("🚀 Starting the labeling server...")
    
    try:
        # Start the web server in background
        print("📡 Starting server on http://localhost:5000")
        print("📝 Opening browser automatically...")
        
        # Start the server
        subprocess.Popen([sys.executable, str(script_path)])
        
        # Wait a moment for server to start
        import time
        time.sleep(3)
        
        # Open browser
        webbrowser.open('http://localhost:5000')
        
        print("\n✅ Web labeling tool started successfully!")
        print("🌐 Open your browser to: http://localhost:5000")
        print("📋 Follow the instructions on the web interface")
        
        return True
        
    except Exception as e:
        print(f"❌ Error starting web tool: {e}")
        return False

def show_quality_check_tools():
    """Show quality checking tools available"""
    
    print("\n🔍 Quality Check Tools Available:")
    print("-" * 50)
    
    print("After labeling, you can use these tools to verify quality:")
    
    print("\n1. 📊 Visual Verification:")
    print("   python3 scripts/visualize_manual_labels.py")
    print("   - Shows your labels overlaid on images")
    
    print("\n2. 📈 Quality Statistics:")
    print("   python3 scripts/get_labeling_stats.py --data model/datasets/manual_labeled")
    print("   - Shows labeling statistics and metrics")
    
    print("\n3. ✅ Quality Check:")
    print("   python3 scripts/check_label_quality.py --data model/datasets/manual_labeled")
    print("   - Checks for common labeling issues")

def show_next_steps():
    """Show next steps after annotation"""
    
    print("\n🚀 Next Steps After Annotation:")
    print("=" * 60)
    
    print("1. ✅ Complete all 29 images with high quality")
    print("2. 🔍 Review and validate all labels")
    print("3. 📊 Run quality check tools")
    print("4. 💾 Backup your labeled dataset")
    print("5. 🏋️ Train new model on manual labels")
    print("6. 🧪 Test performance improvement")
    print("7. 🤖 Deploy for robotic picking")

def main():
    """Main function to guide through manual annotation"""
    
    print("🎯 MANUAL ANNOTATION QUICK START")
    print("=" * 60)
    print("Let's get you started with annotating the Kaggle dataset!")
    print("=" * 60)
    
    # Step 1: Check dataset readiness
    if not check_dataset_ready():
        print("\n❌ Please run the dataset reduction script first:")
        print("python3 scripts/reduce_kaggle_dataset.py")
        return
    
    # Step 2: Show annotation options
    show_annotation_options()
    
    # Step 3: Start the web labeling tool
    print("\n" + "=" * 60)
    choice = input("\nWhich tool would you like to use? (1/2/3) [1]: ").strip() or "1"
    
    if choice == "1":
        if start_web_labeling_tool():
            print("\n🎉 Web labeling tool is ready!")
            print("📝 Start annotating your images")
        else:
            print("\n❌ Failed to start web tool")
            print("🔄 Please try manual setup or choose another tool")
    
    elif choice == "2":
        print("\n🖼️ To use LabelImg:")
        print("1. Install: pip install labelImg")
        print("2. Run: labelImg model/datasets/manual_labeled/train/images/ model/datasets/manual_labeled/data.yaml")
    
    elif choice == "3":
        print("\n🌐 To use CVAT:")
        print("1. Go to https://cvat.org")
        print("2. Create new project")
        print("3. Upload images from model/datasets/manual_labeled/")
    
    # Step 4: Show quality check tools
    show_quality_check_tools()
    
    # Step 5: Show next steps
    show_next_steps()
    
    print("\n" + "=" * 60)
    print("🎯 You're ready to start manual annotation!")
    print("📝 Take your time and focus on quality")
    print("⏰ Expected time: 2-4 hours for all 29 images")
    print("🎯 Goal: Perfect bounding boxes for robotic picking")
    print("=" * 60)

if __name__ == '__main__':
    main()