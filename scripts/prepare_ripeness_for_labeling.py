#!/usr/bin/env python3
"""
PREPARE RIPENESS DATASET FOR MANUAL LABELING
Use existing web labeling tool to add manual labels to ripeness dataset
"""

import shutil
from pathlib import Path
import random

def prepare_ripeness_for_labeling(output_dir="model/datasets/manual_ripeness_to_label", 
                                 sample_size=30):
    """
    Prepare ripeness dataset for manual labeling using existing web tool
    
    Args:
        output_dir: Directory to create for labeling
        sample_size: Number of images to prepare (just a few!)
    """
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Source directories
    ripeness_dataset = Path("model/datasets/overripe_from_kaggle")
    unripe_path = ripeness_dataset / "unripe"
    overripe_path = ripeness_dataset / "overripe"
    
    print("🍓 PREPARING RIPENESS DATASET FOR MANUAL LABELING")
    print("=" * 55)
    print("This will create a dataset ready for your web labeling tool")
    print("Just copy a few images from each ripeness category")
    print("All labeled strawberries will be 'ripe' (class 0)")
    print("=" * 55)
    
    # Count available images
    unripe_images = list(unripe_path.glob("*.jpg")) if unripe_path.exists() else []
    overripe_images = list(overripe_path.glob("*.jpg")) if overripe_path.exists() else []
    
    print(f"📊 Available images:")
    print(f"   Unripe: {len(unripe_images)}")
    print(f"   Overripe: {len(overripe_images)}")
    
    if len(unripe_images) + len(overripe_images) < sample_size:
        print(f"⚠️  Not enough images, reducing sample size to {len(unripe_images) + len(overripe_images)}")
        sample_size = len(unripe_images) + len(overripe_images)
    
    # Select random samples
    selected_images = []
    
    # Sample from unripe (we'll find ripe strawberries in these)
    if unripe_images:
        unripe_sample = random.sample(unripe_images, min(sample_size//2, len(unripe_images)))
        selected_images.extend(unripe_sample)
    
    # Sample from overripe (we'll find ripe strawberries in these)
    if overripe_images:
        overripe_sample = random.sample(overripe_images, min(sample_size//2, len(overripe_images)))
        selected_images.extend(overripe_sample)
    
    # Shuffle for variety
    random.shuffle(selected_images)
    
    print(f"\n🎯 Selected {len(selected_images)} images for labeling:")
    print(f"   From unripe: {len([img for img in selected_images if 'unripe' in str(img)])}")
    print(f"   From overripe: {len([img for img in selected_images if 'overripe' in str(img)])}")
    
    # Copy images to labeling directory
    copied_count = 0
    for i, img_path in enumerate(selected_images):
        # Create new filename with category prefix
        category = 'unripe' if 'unripe' in str(img_path) else 'overripe'
        new_name = f"{category}_{i:03d}_{img_path.name}"
        dest_path = output_path / new_name
        
        try:
            shutil.copy2(img_path, dest_path)
            copied_count += 1
            print(f"✅ Copied: {img_path.name} -> {new_name}")
        except Exception as e:
            print(f"❌ Failed to copy {img_path.name}: {e}")
    
    print(f"\n🎉 PREPARATION COMPLETE!")
    print(f"✅ Copied {copied_count} images to: {output_path}")
    
    # Create instructions
    instructions_path = output_path / "LABELING_INSTRUCTIONS.md"
    with open(instructions_path, 'w') as f:
        f.write("""# Ripeness Dataset Labeling Instructions

## 🍓 What to Label
Label **strawberries only** - ignore other fruits or objects.

## 🎯 Goal
- Find ripe strawberries in unripe/overripe images
- All labeled strawberries are **ripe** (class 0)
- This adds manual ripeness detection to your model

## 📋 Categories
- **Unripe images**: Look for strawberries that look ripe/yellowish
- **Overripe images**: Look for strawberries that still look fresh/red

## ✅ Labeling Tips
1. Draw tight bounding boxes around strawberries
2. Only label strawberries that appear ripe
3. Skip images with no ripe strawberries
4. Use the web tool: `python3 scripts/label_images_web.py model/datasets/manual_ripeness_to_label`

## 🚀 After Labeling
Train a multi-class ripeness detection model:
- Class 0: ripe (your manual labels)
- Class 1: unripe (from Kaggle)
- Class 2: overripe (from Kaggle)

This will give your robotic picker ripeness awareness!
""")
    
    print(f"📋 Created instructions: {instructions_path}")
    
    return {
        'total_images': copied_count,
        'output_directory': str(output_path),
        'next_command': f"python3 scripts/label_images_web.py {output_path}"
    }

def create_ripeness_training_script():
    """Create a script to train ripeness detection model after labeling"""
    
    script_content = '''#!/usr/bin/env python3
"""
TRAIN RIPENESS DETECTION MODEL
Train multi-class ripeness detection after manual labeling
"""

from ultralytics import YOLO
from pathlib import Path

def train_ripeness_model():
    """Train ripeness detection model"""
    
    print("🍓 TRAINING RIPENESS DETECTION MODEL")
    print("=" * 45)
    
    # Dataset configuration
    data_yaml = """
path: model/datasets/manual_ripeness_combined
train: images/train
val: images/val
test: images/test

nc: 3
names: ['ripe', 'unripe', 'overripe']
"""
    
    # Save data.yaml
    data_path = Path("model/datasets/manual_ripeness_combined/data.yaml")
    data_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(data_path, 'w') as f:
        f.write(data_yaml.strip())
    
    print("✅ Created ripeness dataset configuration")
    print("📊 Classes:")
    print("   0: ripe (your manual labels)")
    print("   1: unripe (from Kaggle)")
    print("   2: overripe (from Kaggle)")
    
    print("\\n🚀 Ready to train ripeness detection model!")
    print("Run: yolo train data=model/datasets/manual_ripeness_combined/data.yaml model=yolov8n.pt epochs=50")

if __name__ == '__main__':
    train_ripeness_model()
'''
    
    script_path = Path("scripts/train_ripeness_model.py")
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"📜 Created training script: {script_path}")

def main():
    """Main function"""
    print("🍓 PREPARING RIPENESS DATASET FOR MANUAL LABELING")
    
    # Prepare dataset
    result = prepare_ripeness_for_labeling()
    
    # Create training script
    create_ripeness_training_script()
    
    print(f"\n🎉 SETUP COMPLETE!")
    print(f"=" * 55)
    print(f"📁 Dataset ready: {result['output_directory']}")
    print(f"📊 Images prepared: {result['total_images']}")
    print(f"")
    print(f"🚀 NEXT STEPS:")
    print(f"1. Start web labeling: {result['next_command']}")
    print(f"2. Label strawberries (all will be 'ripe' class)")
    print(f"3. Combine with existing unripe/overripe data")
    print(f"4. Train multi-class ripeness model")
    print(f"")
    print(f"🎯 This will give your robotic picker ripeness awareness!")
    print(f"   - Detect ripe strawberries for picking")
    print(f"   - Avoid unripe/overripe ones")
    print(f"   - Perfect for optimal harvest timing!")

if __name__ == '__main__':
    main()