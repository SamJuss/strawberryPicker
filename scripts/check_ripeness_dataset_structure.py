#!/usr/bin/env python3
"""
CHECK ACTUAL RIPENESS DATASET STRUCTURE
Find all ripeness categories in the Kaggle dataset
"""

from pathlib import Path
import os

def check_ripeness_structure():
    """Check the actual structure of the ripeness dataset"""
    
    dataset_path = Path("model/datasets/overripe_from_kaggle")
    
    print("🔍 CHECKING RIPENESS DATASET STRUCTURE")
    print("=" * 50)
    
    # Check main directory
    print(f"📁 Main dataset path: {dataset_path}")
    print(f"   Exists: {dataset_path.exists()}")
    
    if dataset_path.exists():
        # List all directories and files
        print(f"\n📊 Contents of {dataset_path}:")
        for item in dataset_path.iterdir():
            if item.is_dir():
                print(f"   📂 {item.name}/")
                # Count images in each directory
                image_count = len(list(item.glob("*.jpg")))
                print(f"      🖼️  Images: {image_count}")
                
                # Show first few image names to understand content
                sample_images = list(item.glob("*.jpg"))[:3]
                if sample_images:
                    print(f"      🔍 Sample images:")
                    for img in sample_images:
                        print(f"         - {img.name}")
                        
            elif item.is_file():
                print(f"   📄 {item.name}")
    
    # Check if there might be other ripeness directories elsewhere
    print(f"\n🔎 Searching for other potential ripeness directories...")
    
    # Look for any directories with "ripe" in the name
    for root, dirs, files in os.walk("model/datasets"):
        for dir_name in dirs:
            if "ripe" in dir_name.lower() and "overripe_from_kaggle" not in root:
                full_path = Path(root) / dir_name
                image_count = len(list(full_path.glob("*.jpg")))
                print(f"   📂 Found: {full_path}")
                print(f"      🖼️  Images: {image_count}")
    
    return dataset_path

def suggest_labeling_strategy():
    """Suggest the best labeling strategy based on actual dataset structure"""
    
    dataset_path = Path("model/datasets/overripe_from_kaggle")
    
    # Check what categories actually exist
    categories = []
    if dataset_path.exists():
        for item in dataset_path.iterdir():
            if item.is_dir():
                categories.append(item.name)
    
    print(f"\n🎯 SUGGESTED LABELING STRATEGY")
    print("=" * 50)
    
    if len(categories) == 3:
        print("✅ PERFECT! Found all 3 ripeness categories:")
        for cat in categories:
            print(f"   📂 {cat}")
        print("\n🚀 Strategy: Label a few images from each category")
        print("   - Use existing categories as base")
        print("   - Add manual labels for precision")
        
    elif len(categories) == 2:
        print("⚠️  Found 2 categories (missing one):")
        for cat in categories:
            print(f"   📂 {cat}")
        print(f"\n🚀 Strategy: Work with available categories")
        print("   - Label strawberries in existing categories")
        print("   - Create missing category through manual labeling")
        
        # Suggest which category to create manually
        if 'unripe' in categories and 'overripe' in categories:
            print("   - Missing: 'ripe' → Create through manual labeling")
        elif 'ripe' in categories and 'unripe' in categories:
            print("   - Missing: 'overripe' → Use existing as base")
        elif 'ripe' in categories and 'overripe' in categories:
            print("   - Missing: 'unripe' → Use existing as base")
            
    else:
        print("❓ Found unexpected structure:")
        for cat in categories:
            print(f"   📂 {cat}")
        print(f"\n🚀 Strategy: Adapt to available data")
        print("   - Analyze image content to determine ripeness")
        print("   - Create appropriate categories through labeling")

if __name__ == '__main__':
    check_ripeness_structure()
    suggest_labeling_strategy()