#!/usr/bin/env python3
"""
STRAWBERRY-SPECIFIC RIPENESS LABELING PREPARATION
Use the complete 3-category strawberry ripeness dataset for manual labeling
"""

from pathlib import Path
import shutil
import random

def prepare_strawberry_ripeness_labeling(sample_size_per_category=25):
    """Prepare strawberry-specific ripeness dataset for manual labeling"""
    
    print("🍓 STRAWBERRY-SPECIFIC RIPENESS LABELING PREPARATION")
    print("=" * 60)
    
    # Source directories from the extracted Fruit Ripeness Dataset
    source_dirs = {
        'ripe': Path("model/train/RipeStrawberry"),
        'unripe': Path("model/train/UnripeStrawberry"), 
        'overripe': Path("model/train/RottenStrawberry")  # Using Rotten as overripe
    }
    
    # Check what categories actually exist
    available_categories = {}
    for category, path in source_dirs.items():
        if path.exists():
            images = list(path.glob("*.jpg"))
            available_categories[category] = {
                'path': path,
                'count': len(images)
            }
            print(f"✅ Found {category}: {len(images)} images")
        else:
            print(f"❌ Missing {category}: {path}")
    
    if not available_categories:
        print("❌ No strawberry ripeness categories found!")
        return None
    
    # Create output directory
    output_path = Path("model/datasets/strawberry_ripeness_to_label")
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n🎯 Preparing labeling dataset with {len(available_categories)} categories:")
    
    # Track preparation summary
    preparation_summary = {
        'categories_covered': set(),
        'total_images': 0,
        'images_by_category': {}
    }
    
    # Sample images from each category
    selected_images = []
    
    for category, info in available_categories.items():
        print(f"\n📂 Processing {category} category:")
        
        category_path = info['path']
        total_images = info['count']
        
        # Add to summary
        preparation_summary['categories_covered'].add(category)
        
        # Sample images (use fewer images for quick labeling)
        sample_size = min(sample_size_per_category, total_images)
        images = list(category_path.glob("*.jpg"))
        
        if len(images) >= sample_size:
            sampled = random.sample(images, sample_size)
        else:
            sampled = images
        
        for img_path in sampled:
            selected_images.append({
                'path': img_path,
                'category': category,
                'original_name': img_path.name
            })
        
        # Update summary
        preparation_summary['images_by_category'][category] = len(sampled)
        print(f"   ✅ Sampled {len(sampled)} images from {total_images} available")
    
    # Shuffle for variety
    random.shuffle(selected_images)
    
    # Copy images to labeling directory
    copied_count = 0
    for i, image_info in enumerate(selected_images):
        img_path = image_info['path']
        category = image_info['category']
        original_name = image_info['original_name']
        
        # Create descriptive filename
        new_name = f"{category}_strawberry_{i:03d}_{original_name}"
        dest_path = output_path / new_name
        
        try:
            shutil.copy2(img_path, dest_path)
            copied_count += 1
            print(f"   📸 Copied: {original_name} → {new_name}")
        except Exception as e:
            print(f"   ❌ Failed to copy {original_name}: {e}")
    
    preparation_summary['total_images'] = copied_count
    
    # Create strawberry-specific instructions
    create_strawberry_instructions(output_path, preparation_summary)
    
    # Create strawberry-specific training script
    create_strawberry_training_script(preparation_summary['categories_covered'])
    
    print(f"\n🎉 STRAWBERRY RIPENESS PREPARATION COMPLETE!")
    print(f"✅ Copied {copied_count} images from {len(available_categories)} categories")
    
    return {
        'output_directory': str(output_path),
        'total_images': copied_count,
        'categories': list(preparation_summary['categories_covered']),
        'next_command': f"python3 scripts/label_images_web.py {output_path}"
    }

def create_strawberry_instructions(output_path, summary):
    """Create strawberry-specific labeling instructions"""
    
    instructions_path = output_path / "STRAWBERRY_RIPENESS_INSTRUCTIONS.md"
    
    content = f"""# 🍓 STRAWBERRY RIPENESS LABELING INSTRUCTIONS

## 📊 Dataset Overview
- **Total Images**: {summary['total_images']}
- **Categories**: {', '.join(summary['categories_covered'])}
- **Fruit Type**: Strawberries Only
- **Purpose**: Robotic strawberry harvesting with ripeness awareness

## 🎯 Labeling Goal
Create perfect bounding boxes for **strawberry ripeness detection** to enable your robotic picker to harvest only perfectly ripe strawberries.

## 📋 Ripeness Categories for Strawberries

### **🟢 UNRIPE STRAWBERRIES** (Class 0)
- **Color**: Green, white, or pale pink
- **Texture**: Hard, firm, underdeveloped
- **Size**: Smaller, not fully grown
- **Appearance**: Pointed shape, no red coloration
- **When to label**: Not ready for harvest

### **🟡 RIPE STRAWBERRIES** (Class 1) 
- **Color**: Bright red, uniform color
- **Texture**: Firm but yielding, smooth surface
- **Size**: Full size, plump appearance
- **Appearance**: Rounded shape, glossy surface
- **When to label**: **PERFECT FOR HARVESTING**

### **🔴 OVERRIPE STRAWBERRIES** (Class 2)
- **Color**: Dark red, purple, or brown spots
- **Texture**: Soft, mushy, or wrinkled
- **Appearance**: Sunken areas, dull surface
- **Signs**: Beginning to decay, loss of firmness
- **When to label**: Past optimal harvest time

## ✅ Labeling Instructions

### **🔍 What to Look For:**
1. **Focus on strawberries only** - ignore other fruits in multi-fruit images
2. **Draw tight bounding boxes** around each strawberry
3. **Multiple strawberries per image** - label each one individually
4. **Mixed ripeness** - use different categories for different berries

### **🖱️ Web Tool Controls:**
- **Click & drag** to draw bounding boxes
- **Save & Next** to save and proceed
- **Reset Boxes** to clear current image
- **Previous** to go back

### **⚡ Quick Category Guide:**
- **1 key**: Unripe (green/white)
- **2 key**: Ripe (bright red) ← **TARGET FOR HARVESTING**
- **3 key**: Overripe (dark/soft)
- **S key**: Skip difficult images
- **Q key**: Quit and save

## 🚀 After Labeling

### **Training Command:**
```bash
python3 scripts/train_strawberry_ripeness_model.py
```

### **Expected Classes:**
- **Class 0**: unripe (avoid harvesting)
- **Class 1**: ripe ← **TARGET FOR ROBOTIC PICKING**
- **Class 2**: overripe (avoid harvesting)

## 🎊 Benefits for Robotic Harvesting

### **🤖 Robotic Intelligence**
- **Precision picking**: Only harvest ripe strawberries
- **Quality control**: Avoid unripe/overripe ones
- **Optimal timing**: Perfect ripeness selection
- **Efficiency**: Automated ripeness classification

### **📈 Harvesting Strategy**
- **Greenhouse automation**: Smart harvesting robots
- **Quality assurance**: Consistent ripeness standards
- **Profit maximization**: Harvest at peak ripeness
- **Waste reduction**: Avoid premature or overripe picking

## 🎯 Perfect Ripeness Indicators
Look for strawberries that are:
- **Bright red color** throughout
- **Firm but slightly yielding** to gentle pressure
- **Glossy surface** with fresh appearance
- **Full size** and plump shape
- **No green or white patches**
- **No soft spots or wrinkles**

**🍓🤖 Your robotic picker will have perfect ripeness intelligence for optimal strawberry harvesting!**
"""
    
    with open(instructions_path, 'w') as f:
        f.write(content.strip())
    
    print(f"📋 Created strawberry-specific instructions: {instructions_path}")

def create_strawberry_training_script(categories):
    """Create strawberry-specific training script"""
    
    script_path = Path("scripts/train_strawberry_ripeness_model.py")
    
    # Create class names list
    class_names = sorted(list(categories))
    
    script_content = f'''#!/usr/bin/env python3
"""
STRAWBERRY RIPENESS DETECTION MODEL TRAINING
Train multi-class ripeness detection specifically for strawberries
"""

from ultralytics import YOLO
from pathlib import Path
import yaml

def train_strawberry_ripeness_model():
    """Train strawberry ripeness detection model"""
    
    print("🍓 STRAWBERRY RIPENESS DETECTION MODEL TRAINING")
    print("=" * 60)
    
    # Dataset configuration
    class_names = {class_names}
    
    data_config = {{
        'path': 'model/datasets/strawberry_ripeness_combined',
        'train': 'images/train',
        'val': 'images/val', 
        'test': 'images/test',
        'nc': len(class_names),
        'names': class_names
    }}
    
    # Save data.yaml
    data_path = Path("model/datasets/strawberry_ripeness_combined/data.yaml")
    data_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(data_path, 'w') as f:
        yaml.dump(data_config, f, default_flow_style=False)
    
    print("✅ Created strawberry ripeness dataset configuration")
    print(f"📊 Classes: {{len(class_names)}}")
    for i, name in enumerate(class_names):
        print(f"   Class {{i}}: {{name}}")
    
    print("\\n🚀 Ready to train strawberry ripeness detection model!")
    print("Suggested training commands:")
    print("  yolo train data=model/datasets/strawberry_ripeness_combined/data.yaml model=yolov8n.pt epochs=100 imgsz=640")
    print("  yolo train data=model/datasets/strawberry_ripeness_combined/data.yaml model=yolov8s.pt epochs=100 imgsz=640")
    
    print("\\n🎯 This model will give your robotic picker the intelligence to:")
    print("  ✅ Detect ripe strawberries for harvesting")
    print("  ✅ Avoid unripe strawberries (wait for ripening)")
    print("  ✅ Avoid overripe strawberries (prevent waste)")
    print("  ✅ Optimize harvest timing for maximum quality!")

if __name__ == '__main__':
    import yaml
    train_strawberry_ripeness_model()
'''
    
    with open(script_path, 'w') as f:
        f.write(script_content.strip())
    
    print(f"📜 Created strawberry training script: {script_path}")

def main():
    """Main function"""
    print("🍓 STRAWBERRY-SPECIFIC RIPENESS LABELING PREPARATION")
    
    # Prepare strawberry ripeness labeling
    result = prepare_strawberry_ripeness_labeling(sample_size_per_category=25)
    
    if result:
        print(f"\n🎉 STRAWBERRY SETUP COMPLETE!")
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
        print(f"🎯 This will give your robotic picker perfect strawberry ripeness awareness!")
        print(f"   Perfect for automated greenhouse harvesting with optimal quality!")

if __name__ == '__main__':
    main()