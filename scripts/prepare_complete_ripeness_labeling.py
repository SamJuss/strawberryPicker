#!/usr/bin/env python3
"""
COMPLETE RIPENESS DATASET LABELING PREPARATION
Handle all available ripeness datasets and categories
"""

from pathlib import Path
import shutil
import random

def find_all_ripeness_datasets():
    """Find all available ripeness datasets in the project"""
    
    datasets = []
    base_path = Path("model/datasets")
    
    # Look for ripeness-related datasets
    ripeness_patterns = [
        "overripe_from_kaggle",
        "ripeness_classification_converted", 
        "strawberry_ripeness_classification",
        "ripe_only_detection"
    ]
    
    for pattern in ripeness_patterns:
        dataset_path = base_path / pattern
        if dataset_path.exists():
            # Check what categories exist in this dataset
            categories = []
            for item in dataset_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Count images in category
                    image_count = len(list(item.glob("*.jpg")))
                    if image_count > 0:
                        categories.append({
                            'name': item.name,
                            'path': item,
                            'count': image_count
                        })
            
            if categories:
                datasets.append({
                    'name': pattern,
                    'path': dataset_path,
                    'categories': categories,
                    'total_images': sum(cat['count'] for cat in categories)
                })
    
    return datasets

def prepare_complete_ripeness_labeling(sample_size_per_category=20):
    """Prepare complete ripeness labeling across all available datasets"""
    
    print("🍓 COMPLETE RIPENESS DATASET LABELING PREPARATION")
    print("=" * 60)
    
    # Find all available datasets
    datasets = find_all_ripeness_datasets()
    
    if not datasets:
        print("❌ No ripeness datasets found!")
        return None
    
    print(f"📊 Found {len(datasets)} ripeness datasets:")
    for dataset in datasets:
        print(f"   📁 {dataset['name']}: {dataset['total_images']} images")
        for cat in dataset['categories']:
            print(f"      📂 {cat['name']}: {cat['count']} images")
    
    # Create output directory
    output_path = Path("model/datasets/complete_ripeness_to_label")
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Track what we're preparing
    preparation_summary = {
        'datasets_used': [],
        'categories_covered': set(),
        'total_images': 0,
        'images_by_category': {}
    }
    
    # Sample images from each category across all datasets
    selected_images = []
    
    for dataset in datasets:
        print(f"\n🎯 Processing dataset: {dataset['name']}")
        
        for category in dataset['categories']:
            cat_name = category['name']
            cat_path = category['path']
            cat_count = category['count']
            
            # Add to summary
            preparation_summary['categories_covered'].add(cat_name)
            preparation_summary['datasets_used'].append(dataset['name'])
            
            # Sample images from this category
            sample_size = min(sample_size_per_category, cat_count)
            images = list(cat_path.glob("*.jpg"))
            
            if len(images) >= sample_size:
                sampled = random.sample(images, sample_size)
            else:
                sampled = images
            
            for img_path in sampled:
                selected_images.append({
                    'path': img_path,
                    'dataset': dataset['name'],
                    'category': cat_name,
                    'suggested_category': cat_name  # Use the actual category name
                })
            
            # Update summary
            if cat_name not in preparation_summary['images_by_category']:
                preparation_summary['images_by_category'][cat_name] = 0
            preparation_summary['images_by_category'][cat_name] += len(sampled)
            
            print(f"   ✅ Sampled {len(sampled)} images from {cat_name}")
    
    # Shuffle for variety
    random.shuffle(selected_images)
    
    # Copy images to labeling directory
    copied_count = 0
    for i, image_info in enumerate(selected_images):
        img_path = image_info['path']
        dataset = image_info['dataset']
        category = image_info['category']
        
        # Create descriptive filename
        new_name = f"{category}_{dataset}_{i:03d}_{img_path.name}"
        dest_path = output_path / new_name
        
        try:
            shutil.copy2(img_path, dest_path)
            copied_count += 1
            print(f"   📸 Copied: {img_path.name} → {new_name}")
        except Exception as e:
            print(f"   ❌ Failed to copy {img_path.name}: {e}")
    
    preparation_summary['total_images'] = copied_count
    
    # Create comprehensive instructions
    create_comprehensive_instructions(output_path, preparation_summary)
    
    # Create enhanced training script
    create_enhanced_training_script(preparation_summary['categories_covered'])
    
    print(f"\n🎉 PREPARATION COMPLETE!")
    print(f"✅ Copied {copied_count} images from {len(set(preparation_summary['datasets_used']))} datasets")
    print(f"📂 Categories covered: {', '.join(preparation_summary['categories_covered'])}")
    
    return {
        'output_directory': str(output_path),
        'total_images': copied_count,
        'categories': list(preparation_summary['categories_covered']),
        'next_command': f"python3 scripts/label_images_web.py {output_path}"
    }

def create_comprehensive_instructions(output_path, summary):
    """Create comprehensive labeling instructions"""
    
    instructions_path = output_path / "COMPREHENSIVE_LABELING_INSTRUCTIONS.md"
    
    # Build category-specific instructions
    category_instructions = ""
    for category in summary['categories_covered']:
        if category == 'ripe':
            category_instructions += f"""
### **🟡 Ripe Strawberries**
- **Color**: Bright red, uniform color
- **Texture**: Firm, smooth surface
- **Size**: Full size, plump appearance
- **When to label**: Perfect harvesting condition
"""
        elif category == 'unripe':
            category_instructions += f"""
### **🟢 Unripe Strawberries**
- **Color**: Green, white, or pale pink
- **Texture**: Hard, underdeveloped
- **Size**: Smaller, not fully grown
- **When to label**: Not ready for harvest
"""
        elif category == 'overripe':
            category_instructions += f"""
### **🔴 Overripe Strawberries**
- **Color**: Dark red, purple, or brown spots
- **Texture**: Soft, mushy, or wrinkled
- **Appearance**: Sunken areas, mold, or decay
- **When to label**: Past optimal harvest time
"""
        elif category == 'partially-ripe':
            category_instructions += f"""
### **🟠 Partially Ripe Strawberries**
- **Color**: Mix of green/red or pink/red
- **Texture**: Transitioning from firm to soft
- **Appearance**: Some red areas, some green/white
- **When to label**: In transition phase
"""
    
    content = f"""# 🍓 COMPREHENSIVE RIPENESS LABELING INSTRUCTIONS

## 📊 Dataset Overview
- **Total Images**: {summary['total_images']}
- **Categories**: {', '.join(summary['categories_covered'])}
- **Datasets Used**: {', '.join(set(summary['datasets_used']))}

## 🎯 Labeling Goal
Create perfect bounding boxes for **strawberry ripeness detection** with multiple ripeness levels.

## 📋 Ripeness Categories

{category_instructions}

## ✅ Universal Labeling Tips

### **🔍 What to Look For:**
1. **Focus on strawberries only** - ignore other fruits/objects
2. **Draw tight bounding boxes** around each strawberry
3. **Multiple strawberries per image** - label each one individually
4. **Mixed ripeness** - use different categories for different berries

### **🖱️ Web Tool Controls:**
- **Click & drag** to draw bounding boxes
- **Save & Next** to save and proceed
- **Reset Boxes** to clear current image
- **Previous** to go back

### **⚡ Quick Category Guide:**
- **1 key**: First category (usually unripe)
- **2 key**: Second category (usually ripe) 
- **3 key**: Third category (usually overripe)
- **S key**: Skip difficult images
- **Q key**: Quit and save

## 🚀 After Labeling

### **Training Command:**
```bash
python3 scripts/train_enhanced_ripeness_model.py
```

### **Expected Classes:**
- Class 0: {list(summary['categories_covered'])[0] if summary['categories_covered'] else 'unripe'}
- Class 1: {list(summary['categories_covered'])[1] if len(summary['categories_covered']) > 1 else 'ripe'}
- Class 2: {list(summary['categories_covered'])[2] if len(summary['categories_covered']) > 2 else 'overripe'}

## 🎊 Benefits
- **🤖 Robotic Precision**: Your picker will know exact ripeness
- **⏰ Optimal Harvesting**: Pick only perfectly ripe strawberries
- **📈 Quality Control**: Consistent ripeness selection
- **🧠 Smart Automation**: Multi-class ripeness awareness

**🍓🤖 Ready to create the ultimate ripeness-aware strawberry detection system!**
"""
    
    with open(instructions_path, 'w') as f:
        f.write(content.strip())
    
    print(f"📋 Created comprehensive instructions: {instructions_path}")

def create_enhanced_training_script(categories):
    """Create enhanced training script for multi-class ripeness detection"""
    
    script_path = Path("scripts/train_enhanced_ripeness_model.py")
    
    # Create class names list
    class_names = sorted(list(categories))
    
    script_content = f'''#!/usr/bin/env python3
"""
ENHANCED RIPENESS DETECTION MODEL TRAINING
Train multi-class ripeness detection with all available categories
"""

from ultralytics import YOLO
from pathlib import Path
import yaml

def train_enhanced_ripeness_model():
    """Train enhanced ripeness detection model"""
    
    print("🍓 ENHANCED RIPENESS DETECTION MODEL TRAINING")
    print("=" * 55)
    
    # Dataset configuration
    class_names = {class_names}
    
    data_config = {{
        'path': 'model/datasets/complete_ripeness_combined',
        'train': 'images/train',
        'val': 'images/val', 
        'test': 'images/test',
        'nc': len(class_names),
        'names': class_names
    }}
    
    # Create data.yaml
    data_path = Path("model/datasets/complete_ripeness_combined/data.yaml")
    data_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(data_path, 'w') as f:
        yaml.dump(data_config, f, default_flow_style=False)
    
    print("✅ Created enhanced ripeness dataset configuration")
    print(f"📊 Classes: {{len(class_names)}}")
    for i, name in enumerate(class_names):
        print(f"   Class {{i}}: {{name}}")
    
    print("\\n🚀 Ready to train enhanced ripeness detection model!")
    print("Suggested training commands:")
    print("  yolo train data=model/datasets/complete_ripeness_combined/data.yaml model=yolov8n.pt epochs=100 imgsz=640")
    print("  yolo train data=model/datasets/complete_ripeness_combined/data.yaml model=yolov8s.pt epochs=100 imgsz=640")

if __name__ == '__main__':
    import yaml
    train_enhanced_ripeness_model()
'''
    
    with open(script_path, 'w') as f:
        f.write(script_content.strip())
    
    print(f"📜 Created enhanced training script: {script_path}")

def main():
    """Main function"""
    print("🍓 COMPLETE RIPENESS DATASET LABELING PREPARATION")
    
    # Prepare complete ripeness labeling
    result = prepare_complete_ripeness_labeling(sample_size_per_category=15)
    
    if result:
        print(f"\n🎉 SETUP COMPLETE!")
        print(f"=" * 60)
        print(f"📁 Dataset ready: {result['output_directory']}")
        print(f"📊 Total images: {result['total_images']}")
        print(f"📂 Categories: {', '.join(result['categories'])}")
        print(f"")
        print(f"🚀 NEXT STEPS:")
        print(f"1. Start web labeling: {result['next_command']}")
        print(f"2. Label strawberries with appropriate ripeness categories")
        print(f"3. Train enhanced multi-class ripeness model")
        print(f"")
        print(f"🎯 This will create the most comprehensive ripeness detection system!")
        print(f"   Perfect for robotic strawberry harvesting with ripeness awareness!")

if __name__ == '__main__':
    main()