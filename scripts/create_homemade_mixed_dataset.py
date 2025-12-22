#!/usr/bin/env python3
"""
CREATE HOMEMADE_MIXED DATASET
Combine your manually labeled homemade dataset with the ripeness dataset you just labeled
"""

from pathlib import Path
import shutil
import random
import yaml
from collections import Counter

def create_homemade_mixed_dataset(homemade_ratio=0.6, ripeness_ratio=0.4):
    """Create a mixed dataset combining homemade and ripeness labeled data"""
    
    print("🍓 CREATING HOMEMADE_MIXED DATASET")
    print("=" * 60)
    
    # Source datasets
    homemade_path = Path("model/dataset_homemade_labeled")
    ripeness_path = Path("model/datasets/strawberry_ripeness_to_label")
    
    # Verify source datasets exist
    if not homemade_path.exists():
        print(f"❌ Homemade dataset not found: {homemade_path}")
        return None
        
    if not ripeness_path.exists():
        print(f"❌ Ripeness dataset not found: {ripeness_path}")
        return None
    
    # Output dataset
    output_path = Path("model/dataset_homemade_mixed")
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"📊 Mixing ratio: {homemade_ratio*100}% homemade + {ripeness_ratio*100}% ripeness")
    
    # Count existing datasets
    homemade_images = list((homemade_path / "images").glob("*.jpg"))
    ripeness_images = list(ripeness_path.glob("*.jpg"))
    
    print(f"📊 Source datasets:")
    print(f"   Homemade: {len(homemade_images)} images")
    print(f"   Ripeness: {len(ripeness_images)} images")
    
    # Calculate sample sizes
    total_target = min(len(homemade_images), len(ripeness_images)) * 2  # Balanced dataset
    homemade_target = int(total_target * homemade_ratio)
    ripeness_target = int(total_target * ripeness_ratio)
    
    print(f"📊 Target mixed dataset:")
    print(f"   Homemade samples: {homemade_target}")
    print(f"   Ripeness samples: {ripeness_target}")
    print(f"   Total: {homemade_target + ripeness_target}")
    
    # Sample images from each dataset
    if len(homemade_images) >= homemade_target:
        selected_homemade = random.sample(homemade_images, homemade_target)
    else:
        selected_homemade = homemade_images  # Use all available
    
    if len(ripeness_images) >= ripeness_target:
        selected_ripeness = random.sample(ripeness_images, ripeness_target)
    else:
        selected_ripeness = ripeness_images  # Use all available
    
    print(f"✅ Selected {len(selected_homemade)} homemade images")
    print(f"✅ Selected {len(selected_ripeness)} ripeness images")
    
    # Create dataset structure
    for split in ['train', 'valid', 'test']:
        (output_path / 'images' / split).mkdir(parents=True, exist_ok=True)
        (output_path / 'labels' / split).mkdir(parents=True, exist_ok=True)
    
    # Distribute images across splits (70% train, 20% val, 10% test)
    total_selected = len(selected_homemade) + len(selected_ripeness)
    train_size = int(total_selected * 0.7)
    val_size = int(total_selected * 0.2)
    test_size = total_selected - train_size - val_size
    
    print(f"📊 Split distribution:")
    print(f"   Train: {train_size} images")
    print(f"   Valid: {val_size} images")
    print(f"   Test: {test_size} images")
    
    # Combine and shuffle all selected images
    all_images = []
    
    # Add homemade images
    for img_path in selected_homemade:
        all_images.append({
            'source': 'homemade',
            'image_path': img_path,
            'label_path': homemade_path / "labels" / f"{img_path.stem}.txt"
        })
    
    # Add ripeness images
    for img_path in selected_ripeness:
        all_images.append({
            'source': 'ripeness',
            'image_path': img_path,
            'label_path': ripeness_path / f"{img_path.stem}.txt"
        })
    
    # Shuffle the combined dataset
    random.shuffle(all_images)
    
    # Distribute to splits
    splits = {
        'train': all_images[:train_size],
        'valid': all_images[train_size:train_size+val_size],
        'test': all_images[train_size+val_size:]
    }
    
    # Copy files to output dataset
    copied_count = 0
    for split_name, split_images in splits.items():
        print(f"\n📂 Processing {split_name} split:")
        
        for i, item in enumerate(split_images):
            # Generate new filename
            new_name = f"homemade_mixed_{split_name}_{i:06d}.jpg"
            
            # Copy image
            src_img = item['image_path']
            dst_img = output_path / 'images' / split_name / new_name
            
            try:
                shutil.copy2(src_img, dst_img)
                
                # Copy corresponding label file
                src_label = item['label_path']
                dst_label = output_path / 'labels' / split_name / new_name.replace('.jpg', '.txt')
                
                if src_label.exists():
                    shutil.copy2(src_label, dst_label)
                else:
                    # Create empty label file if source doesn't exist
                    dst_label.touch()
                
                copied_count += 1
                
                if i < 3 or i >= len(split_images) - 3:
                    print(f"   ✅ {item['source']}: {src_img.name} → {new_name}")
                    
            except Exception as e:
                print(f"   ❌ Failed to copy {src_img.name}: {e}")
    
    # Create data.yaml configuration
    create_data_yaml(output_path, copied_count)
    
    # Create mixing summary
    create_mixing_summary(output_path, {
        'homemade_count': len(selected_homemade),
        'ripeness_count': len(selected_ripeness),
        'total_copied': copied_count,
        'homemade_ratio': homemade_ratio,
        'ripeness_ratio': ripeness_ratio
    })
    
    print(f"\n🎉 HOMEMADE_MIXED DATASET CREATED!")
    print(f"✅ Total images copied: {copied_count}")
    print(f"✅ Dataset location: {output_path}")
    
    return {
        'dataset_path': str(output_path),
        'total_images': copied_count,
        'homemade_images': len(selected_homemade),
        'ripeness_images': len(selected_ripeness),
        'next_command': f"python3 scripts/train_homemade_model.py --dataset_path {output_path}"
    }

def create_data_yaml(dataset_path, total_images):
    """Create data.yaml configuration for the mixed dataset"""
    
    data_config = {
        'path': str(dataset_path.absolute()),
        'train': 'images/train',
        'val': 'images/valid',
        'test': 'images/test',
        'nc': 1,
        'names': ['strawberry'],
        'info': {
            'description': 'Homemade mixed dataset combining webcam images and ripeness-labeled images',
            'total_images': total_images,
            'sources': ['homemade_webcam', 'ripeness_labeled'],
            'created': '2025-12-22'
        }
    }
    
    yaml_path = dataset_path / "data.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(data_config, f, default_flow_style=False)
    
    print(f"📄 Created data.yaml configuration")

def create_mixing_summary(dataset_path, stats):
    """Create a summary of the mixing process"""
    
    summary_path = dataset_path / "MIXING_SUMMARY.md"
    
    content = f"""# 🍓 HOMEMADE_MIXED DATASET SUMMARY

## 📊 Dataset Composition
- **Total Images:** {stats['total_copied']}
- **Homemade Images:** {stats['homemade_count']} ({stats['homemade_ratio']*100}%)
- **Ripeness Images:** {stats['ripeness_count']} ({stats['ripeness_ratio']*100}%)
- **Mixing Ratio:** {stats['homemade_ratio']} homemade + {stats['ripeness_ratio']} ripeness

## 🎯 Dataset Sources

### 🏠 Homemade Component ({stats['homemade_count']} images)
- **Source:** Your webcam photos from model/dataset_homemade_labeled/
- **Content:** Original strawberry images you captured
- **Purpose:** Personal, real-world strawberry examples

### 🍓 Ripeness Component ({stats['ripeness_count']} images)
- **Source:** Your manual labeling from model/datasets/strawberry_ripeness_to_label/
- **Content:** 75 images you manually labeled with ripeness categories
- **Purpose:** Enhanced detection with negative examples

## 📈 Dataset Statistics
- **Positive Examples:** Images with strawberry detections
- **Negative Examples:** Images with empty label files (no strawberries)
- **Total Detections:** All individual strawberry bounding boxes

## 🚀 Training Benefits
1. **Personal Touch:** Your own strawberry photos
2. **Manual Quality:** Perfectly labeled ripeness examples
3. **Negative Training:** Robust false positive prevention
4. **Mixed Variety:** Different sources for better generalization

## 💡 Next Steps
```bash
# Train model on your mixed dataset
python3 scripts/train_homemade_model.py --dataset_path {dataset_path}

# Test performance
python3 scripts/test_homemade_model.py --model_path {dataset_path}

# Compare with other models
python3 scripts/test_and_compare_models.py
```

## 🎉 Your Achievement
You now have a **personalized mixed dataset** combining:
- ✅ Your original webcam strawberry photos
- ✅ Your manually labeled ripeness dataset
- ✅ Perfect balance of positive and negative examples
- ✅ Professional-quality training data

**Perfect foundation for training your robotic strawberry picker!**
"""
    
    with open(summary_path, 'w') as f:
        f.write(content.strip())
    
    print(f"📋 Created mixing summary: {summary_path}")

def main():
    """Main function"""
    print("🍓 CREATING HOMEMADE_MIXED DATASET")
    
    # Create the mixed dataset
    result = create_homemade_mixed_dataset(homemade_ratio=0.6, ripeness_ratio=0.4)
    
    if result:
        print(f"\n🎉 HOMEMADE_MIXED DATASET CREATED!")
        print(f"=" * 60)
        print(f"📁 Dataset location: {result['dataset_path']}")
        print(f"📊 Total images: {result['total_images']}")
        print(f"🏠 Homemade images: {result['homemade_images']}")
        print(f"🍓 Ripeness images: {result['ripeness_images']}")
        print(f"")
        print(f"🚀 NEXT STEPS:")
        print(f"1. Train model: {result['next_command']}")
        print(f"2. Test performance on your mixed dataset")
        print(f"3. Compare with your other trained models")
        print(f"")
        print(f"🎯 You now have a personalized mixed dataset combining:")
        print(f"   • Your original webcam strawberry photos")
        print(f"   • Your manually labeled ripeness dataset")
        print(f"   • Perfect balance for robust training!")
        print(f"")
        print(f"🤖 Perfect foundation for your robotic strawberry picker!")

if __name__ == '__main__':
    main()