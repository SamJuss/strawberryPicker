#!/usr/bin/env python3
"""
COMPLETE STRAWBERRY RIPENESS DATASET PREPARATION
Use the complete Fruit Ripeness Dataset with all 3 categories
"""

from pathlib import Path
import shutil
import random

def prepare_complete_strawberry_ripeness(sample_size_per_category=25):
    """Prepare complete strawberry ripeness dataset for manual labeling"""
    
    print("🍓 COMPLETE STRAWBERRY RIPENESS DATASET PREPARATION")
    print("=" * 60)
    
    # Source directories from the extracted Fruit Ripeness Dataset
    source_dirs = {
        'ripe': Path("model/train/RipeStrawberry"),
        'unripe': Path("model/train/UnripeStrawberry"), 
        'overripe': Path("model/train/RottenStrawberry")
    }
    
    # Check what categories are available
    available_categories = {}
    for category, path in source_dirs.items():
        if path.exists():
            images = list(path.glob("*.jpg"))
            available_categories[category] = {
                'path': path,
                'count': len(images)
            }
            print(f"✅ Found {len(images)} {category} strawberry images")
        else:
            print(f"❌ {category} directory not found: {path}")
    
    if not available_categories:
        print("❌ No strawberry ripeness categories found!")
        return None
    
    # Create output directory
    output_path = Path("model/datasets/complete_strawberry_ripeness_to_label")
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Track preparation summary
    preparation_summary = {
        'categories_covered': [],
        'total_images': 0,
        'images_by_category': {}
    }
    
    selected_images = []
    
    # Sample images from each available category
    for category, info in available_categories.items():
        cat_path = info['path']
        cat_count = info['count']
        
        # Sample size (adjust based on available images)
        sample_size = min(sample_size_per_category, cat_count)
        
        print(f"\n🎯 Processing {category} strawberries:")
        print(f"   Available: {cat_count} images")
        print(f"   Sampling: {sample_size} images")
        
        # Get all images and sample randomly
        all_images = list(cat_path.glob("*.jpg"))
        
        if len(all_images) >= sample_size:
            sampled = random.sample(all_images, sample_size)
        else:
            sampled = all_images
        
        for img_path in sampled:
            selected_images.append({
                'path': img_path,
                'category': category,
                'original_name': img_path.name
            })
        
        # Update summary
        preparation_summary['categories_covered'].append(category)
        preparation_summary['images_by_category'][category] = len(sampled)
        preparation_summary['total_images'] += len(sampled)
        
        print(f"   ✅ Sampled {len(sampled)} images")
    
    # Shuffle for variety
    random.shuffle(selected_images)
    
    # Copy images to labeling directory
    copied_count = 0
    for i, image_info in enumerate(selected_images):
        img_path = image_info['path']
        category = image_info['category']
        original_name = image_info['original_name']
        
        # Create descriptive filename
        new_name = f"{category}_{i:03d}_{original_name}"
        dest_path = output_path / new_name
        
        try:
            shutil.copy2(img_path, dest_path)
            copied_count += 1
            if i < 5:  # Show first few copies
                print(f"   📸 Copied: {original_name} → {new_name}")
        except Exception as e:
            print(f"   ❌ Failed to copy {original_name}: {e}")
    
    print(f"\n✅ Successfully copied {copied_count} images")
    
    # Create comprehensive instructions
    create_strawberry_ripeness_instructions(output_path, preparation_summary)
    
    # Create training script
    create_strawberry_ripeness_training_script(preparation_summary['categories_covered'])
    
    return {
        'output_directory': str(output_path),
        'total_images': copied_count,
        'categories': preparation_summary['categories_covered'],
        'next_command': f"python3 scripts/label_images_web.py {output_path}"
    }

def create_strawberry_ripeness_instructions(output_path, summary):
    """Create comprehensive strawberry ripeness labeling instructions"""
    
    instructions_path = output_path / "STRAWBERRY_RIPENESS_LABELING_GUIDE.md"
    
    content = f"""# 🍓 STRAWBERRY RIPENESS LABELING GUIDE

## 📊 Dataset Overview
- **Total Images**: {summary['total_images']}
- **Categories**: {', '.join(summary['categories_covered'])}
- **Source**: Complete Fruit Ripeness Dataset
- **Purpose**: Perfect ripeness detection for robotic strawberry harvesting

## 🎯 Labeling Goal
Create precise bounding boxes around **strawberries only** to train a multi-class ripeness detection model.

## 📋 Ripeness Categories Guide

### 🟢 **Unripe Strawberries** (Class 0)
- **Color**: Green, white, or very pale pink
- **Texture**: Hard, firm to touch
- **Size**: Smaller, underdeveloped
- **Appearance**: No red coloration, may have green patches
- **Harvest Status**: **NOT READY** - too early

### 🟡 **Ripe Strawberries** (Class 1) 
- **Color**: Bright, uniform red
- **Texture**: Firm but not hard, slight give when pressed
- **Size**: Full size, plump and developed
- **Appearance**: Vibrant red color, glossy surface
- **Harvest Status**: **PERFECT** - optimal picking time

### 🔴 **Overripe Strawberries** (Class 2)
- **Color**: Dark red, purple, or brown spots
- **Texture**: Soft, mushy, or wrinkled
- **Appearance**: Sunken areas, dull surface, possible mold
- **Shape**: May be misshapen or collapsing
- **Harvest Status**: **TOO LATE** - past optimal time

## ✅ Labeling Instructions

### **🖱️ Web Tool Controls:**
- **Click & drag** to draw tight bounding boxes
- **Number keys (1,2,3)** to select ripeness category
- **Save & Next** to save and proceed
- **Reset Boxes** to clear current image
- **Previous** to go back if needed

### **📏 Box Drawing Tips:**
1. **Draw tight boxes** - hug the strawberry outline closely
2. **Include entire berry** - don't cut off any parts
3. **Multiple berries** - label each strawberry individually
4. **Mixed ripeness** - use different categories for different berries
5. **Partial berries** - only label if >50% visible

### **🎯 What to Label:**
- ✅ **Whole strawberries** with clear ripeness characteristics
- ✅ **Multiple strawberries** in same image (different boxes)
- ✅ **Partially visible** berries if ripeness is clear
- ❌ **Other fruits** (apples, bananas, etc.) - skip these
- ❌ **Very blurry** or unclear images
- ❌ **Tiny strawberries** (<10% of image)

### **🔍 Quick Category Selection:**
- **Press 1**: Unripe (green/white)
- **Press 2**: Ripe (bright red) 
- **Press 3**: Overripe (dark/rotting)
- **Press S**: Skip difficult images

## 🚀 After Labeling

### **Training Command:**
```bash
python3 scripts/train_strawberry_ripeness_model.py
```

### **Expected Performance:**
- **3-class ripeness detection**: unripe, ripe, overripe
- **Precision harvesting**: Only pick ripe strawberries
- **Quality control**: Avoid unripe/overripe ones
- **Robotic automation**: Perfect for greenhouse harvesting

## 🎊 Benefits for Your Robotic Picker

### **🤖 Smart Harvesting:**
- **Optimal timing**: Pick only perfectly ripe berries
- **Quality assurance**: Consistent ripeness selection
- **Efficiency**: Automated ripeness classification
- **Profit maximization**: Harvest at peak value

### **🧠 AI Intelligence:**
- **Multi-class detection**: Distinguish all ripeness levels
- **Real-time processing**: Fast ripeness assessment
- **Adaptable**: Works in various lighting conditions
- **Scalable**: Handle multiple berries simultaneously

---

**🍓🤖 Your robotic strawberry picker will have complete ripeness intelligence!**
**Perfect for automated greenhouse harvesting with optimal quality control!**
"""
    
    with open(instructions_path, 'w') as f:
        f.write(content.strip())
    
    print(f"📋 Created comprehensive instructions: {instructions_path}")

def create_strawberry_ripeness_training_script(categories):
    """Create training script for strawberry ripeness detection"""
    
    script_path = Path("scripts/train_strawberry_ripeness_model.py")
    
    # Create class names mapping
    class_mapping = {
        'unripe': 0,
        'ripe': 1, 
        'overripe': 2
    }
    
    script_content = f'''#!/usr/bin/env python3
"""
STRAWBERRY RIPENESS DETECTION MODEL TRAINING
Train multi-class ripeness detection for robotic harvesting
"""

from ultralytics import YOLO
from pathlib import Path
import yaml

def train_strawberry_ripeness_model():
    """Train strawberry ripeness detection model"""
    
    print("🍓 STRAWBERRY RIPENESS DETECTION MODEL TRAINING")
    print("=" * 55)
    
    # Dataset configuration
    class_names = ['unripe', 'ripe', 'overripe']
    
    data_config = {{
        'path': 'model/datasets/complete_strawberry_ripeness_combined',
        'train': 'images/train',
        'val': 'images/val', 
        'test': 'images/test',
        'nc': len(class_names),
        'names': class_names
    }}
    
    # Create data.yaml
    data_path = Path("model/datasets/complete_strawberry_ripeness_combined/data.yaml")
    data_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(data_path, 'w') as f:
        yaml.dump(data_config, f, default_flow_style=False)
    
    print("✅ Created strawberry ripeness dataset configuration")
    print(f"📊 Classes: {{len(class_names)}}")
    for i, name in enumerate(class_names):
        print(f"   Class {{i}}: {{name}}")
    
    print("\\n🚀 Ready to train strawberry ripeness detection model!")
    print("Suggested training commands:")
    print("  # Quick training (50 epochs):")
    print("  yolo train data=model/datasets/complete_strawberry_ripeness_combined/data.yaml model=yolov8n.pt epochs=50 imgsz=640")
    print("")
    print("  # Full training (100 epochs):")
    print("  yolo train data=model/datasets/complete_strawberry_ripeness_combined/data.yaml model=yolov8s.pt epochs=100 imgsz=640")
    print("")
    print("  # Production training (150 epochs):")
    print("  yolo train data=model/datasets/complete_strawberry_ripeness_combined/data.yaml model=yolov8m.pt epochs=150 imgsz=640")

if __name__ == '__main__':
    import yaml
    train_strawberry_ripeness_model()
'''
    
    with open(script_path, 'w') as f:
        f.write(script_content.strip())
    
    print(f"📜 Created strawberry ripeness training script: {script_path}")

def main():
    """Main function"""
    print("🍓 COMPLETE STRAWBERRY RIPENESS DATASET PREPARATION")
    
    # Prepare complete strawberry ripeness dataset
    result = prepare_complete_strawberry_ripeness(sample_size_per_category=25)
    
    if result:
        print(f"\n🎉 SETUP COMPLETE!")
        print(f"=" * 60)
        print(f"📁 Dataset ready: {result['output_directory']}")
        print(f"📊 Total images: {result['total_images']}")
        print(f"📂 Categories: {', '.join(result['categories'])}")
        print(f"")
        print(f"🚀 NEXT STEPS:")
        print(f"1. Start web labeling: {result['next_command']}")
        print(f"2. Label strawberries with ripeness categories")
        print(f"3. Train strawberry ripeness detection model")
        print(f"")
        print(f"🎯 This will create the ultimate strawberry ripeness detection system!")
        print(f"   Perfect for robotic strawberry harvesting with ripeness awareness!")

if __name__ == '__main__':
    main()