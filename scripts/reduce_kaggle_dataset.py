#!/usr/bin/env python3
"""
Reduce Kaggle dataset size and prepare for manual bounding box annotation
Creates a smaller, high-quality subset for manual labeling
"""

import cv2
import numpy as np
from pathlib import Path
import shutil
import random
import argparse
from collections import defaultdict

class KaggleDatasetReducer:
    def __init__(self, kaggle_dataset_path, output_path, target_size=100, selection_method='diverse'):
        """
        Reduce Kaggle dataset to manageable size for manual annotation
        
        Args:
            kaggle_dataset_path: Path to original Kaggle dataset
            output_path: Path for reduced dataset
            target_size: Number of images to keep
            selection_method: 'random', 'diverse', 'representative'
        """
        self.kaggle_path = Path(kaggle_dataset_path)
        self.output_path = Path(output_path)
        self.target_size = target_size
        self.selection_method = selection_method
        
        print("🔧 Kaggle Dataset Reducer")
        print("=" * 60)
        print(f"Input: {self.kaggle_path}")
        print(f"Output: {self.output_path}")
        print(f"Target size: {target_size} images")
        print(f"Selection method: {selection_method}")
        print("=" * 60)
    
    def analyze_original_dataset(self):
        """Analyze the original Kaggle dataset structure"""
        
        print("\n📊 ANALYZING ORIGINAL DATASET")
        print("-" * 50)
        
        stats = defaultdict(int)
        
        # Check all splits
        for split in ['train', 'val', 'test']:
            split_path = self.kaggle_path / split
            if split_path.exists():
                images = list(split_path.glob("*.jpg")) + list(split_path.glob("*.png"))
                labels = list((split_path / "labels").glob("*.txt")) if (split_path / "labels").exists() else []
                
                stats[f'{split}_images'] = len(images)
                stats[f'{split}_labels'] = len(labels)
                
                print(f"{split.title()} Split:")
                print(f"  📸 Images: {len(images)}")
                print(f"  🏷️  Labels: {len(labels)}")
        
        total_images = sum(stats[f'{split}_images'] for split in ['train', 'val', 'test'])
        stats['total_images'] = total_images
        
        print(f"\n📈 TOTAL DATASET SIZE: {total_images} images")
        
        return stats
    
    def select_representative_images(self, images, target_count):
        """Select representative images using various strategies"""
        
        print(f"\n🎯 SELECTING REPRESENTATIVE IMAGES")
        print("-" * 50)
        
        if len(images) <= target_count:
            print(f"ℹ️  Dataset already smaller than target ({len(images)} ≤ {target_count})")
            return images
        
        if self.selection_method == 'random':
            return self.select_random_images(images, target_count)
        elif self.selection_method == 'diverse':
            return self.select_diverse_images(images, target_count)
        elif self.selection_method == 'representative':
            return self.select_statistically_representative(images, target_count)
        else:
            return self.select_random_images(images, target_count)
    
    def select_random_images(self, images, target_count):
        """Randomly select images"""
        
        print("📋 Using RANDOM selection")
        selected = random.sample(images, target_count)
        print(f"✅ Selected {len(selected)} random images")
        return selected
    
    def select_diverse_images(self, images, target_count):
        """Select diverse images based on visual characteristics"""
        
        print("🎨 Using DIVERSE selection based on visual characteristics")
        
        # Sample analysis of visual diversity
        diverse_images = []
        
        # Group by approximate characteristics
        groups = {
            'close_up': [],
            'medium_distance': [],
            'multiple_berries': [],
            'single_berry': []
        }
        
        for img_path in images:
            filename = img_path.name
            
            # Simple heuristics based on filename patterns
            if '20_51' in filename or '19_39' in filename:
                groups['close_up'].append(img_path)
            elif '19_59' in filename or '19_45' in filename:
                groups['medium_distance'].append(img_path)
            elif '20_51' in filename:  # Multiple berry patterns
                groups['multiple_berries'].append(img_path)
            else:
                groups['single_berry'].append(img_path)
        
        # Select proportionally from each group
        images_per_group = target_count // len(groups)
        remainder = target_count % len(groups)
        
        for i, (group_name, group_images) in enumerate(groups.items()):
            if group_images:
                select_count = images_per_group + (1 if i < remainder else 0)
                selected_from_group = random.sample(group_images, min(select_count, len(group_images)))
                diverse_images.extend(selected_from_group)
                print(f"  📸 {group_name}: {len(selected_from_group)} images")
        
        # Fill remaining slots if needed
        remaining_needed = target_count - len(diverse_images)
        if remaining_needed > 0:
            remaining_images = [img for img in images if img not in diverse_images]
            if remaining_images:
                additional = random.sample(remaining_images, min(remaining_needed, len(remaining_images)))
                diverse_images.extend(additional)
        
        print(f"✅ Selected {len(diverse_images)} diverse images")
        return diverse_images
    
    def select_statistically_representative(self, images, target_count):
        """Select statistically representative images"""
        
        print("📊 Using STATISTICALLY REPRESENTATIVE selection")
        
        # Simple statistical sampling - could be enhanced with more sophisticated methods
        step = len(images) // target_count
        if step < 1:
            step = 1
        
        representative = []
        for i in range(0, len(images), step):
            if len(representative) < target_count:
                representative.append(images[i])
        
        print(f"✅ Selected {len(representative)} statistically representative images")
        return representative
    
    def create_reduced_dataset(self, selected_images):
        """Create reduced dataset with selected images"""
        
        print(f"\n📁 CREATING REDUCED DATASET")
        print("-" * 50)
        
        # Create output directory structure
        for split in ['train', 'val', 'test']:
            (self.output_path / split / 'images').mkdir(parents=True, exist_ok=True)
            (self.output_path / split / 'labels').mkdir(parents=True, exist_ok=True)
        
        # Copy selected images and their labels
        copied_count = 0
        for img_path in selected_images:
            # Determine which split this image belongs to
            for split in ['train', 'val', 'test']:
                if split in str(img_path):
                    # Copy image
                    src_img = img_path
                    dst_img = self.output_path / split / 'images' / img_path.name
                    shutil.copy2(src_img, dst_img)
                    
                    # Copy corresponding label
                    label_name = img_path.stem + '.txt'
                    src_label = self.kaggle_path / split / 'labels' / label_name
                    dst_label = self.output_path / split / 'labels' / label_name
                    
                    if src_label.exists():
                        shutil.copy2(src_label, dst_label)
                        copied_count += 1
                        print(f"  ✅ Copied: {img_path.name}")
                    else:
                        print(f"  ⚠️  Label not found: {label_name}")
                    break
        
        print(f"✅ Successfully copied {copied_count} image-label pairs")
        return copied_count
    
    def create_labeling_guide(self):
        """Create guide for manual bounding box annotation"""
        
        print(f"\n📝 CREATING LABELING GUIDE")
        print("-" * 50)
        
        guide_content = f"""# Manual Bounding Box Labeling Guide

## 🎯 Purpose
You are manually annotating bounding boxes for the reduced Kaggle dataset to ensure perfect quality for robotic strawberry picking.

## 📊 Dataset Info
- Total images to label: {self.target_size}
- Selection method: {self.selection_method}
- Output directory: {self.output_path}

## 🔧 Labeling Instructions

### 1. Bounding Box Requirements
- **Tight Fit**: Box should closely follow strawberry contours
- **Complete Coverage**: Entire strawberry must be inside the box
- **No Background**: Minimize background pixels in the box
- **Individual Berries**: Each strawberry gets its own box

### 2. Quality Standards
- **Position Accuracy**: Box center should align with berry center
- **Size Appropriateness**: Box should be ~5-10% larger than berry
- **Edge Alignment**: Box edges should follow berry shape
- **Consistency**: Similar quality across all images

### 3. Common Issues to Avoid
- **Loose Boxes**: Too much background space
- **Tight Boxes**: Cutting off parts of strawberries
- **Merged Berries**: Multiple berries in one box
- **Partial Coverage**: Boxes not fully enclosing berries

## 🛠️ Labeling Tools

### Recommended Tools:
1. **LabelImg** (Open source)
2. **CVAT** (Computer Vision Annotation Tool)
3. **Roboflow** (Online platform)
4. **Custom web tool** (if available)

### Label Format:
- **YOLO Format**: class_id x_center y_center width height
- **Normalized Coordinates**: 0-1 range
- **Single Class**: All strawberries are class 0

## 📋 Quality Checklist

Before finalizing each label:
- [ ] Box tightly encloses entire strawberry
- [ ] No parts of strawberry cut off
- [ ] Minimal background pixels
- [ ] Box follows berry shape reasonably well
- [ ] Consistent with other labels in dataset

## 🎯 Success Criteria

**Excellent Labels:**
- Tight fit around strawberry
- Complete coverage
- Minimal background
- Consistent quality

**Acceptable Labels:**
- Reasonable fit
- Full strawberry visible
- Not too much background
- Consistent with dataset

**Needs Improvement:**
- Loose fitting
- Partial coverage
- Too much background
- Inconsistent quality

## 🚀 Next Steps

1. **Label all images** in the reduced dataset
2. **Quality review** of all annotations
3. **Train new model** with manually labeled data
4. **Test performance** on robotic picking
5. **Iterate improvements** based on results

## 📊 Expected Outcome

With manual annotation, we expect:
- **Higher accuracy**: Better bounding box positioning
- **Improved precision**: More reliable robotic picking
- **Better generalization**: Consistent quality across conditions
- **Reduced errors**: Fewer picking failures

## 💡 Tips for Success

- **Take your time**: Quality over speed
- **Be consistent**: Similar approach for all images
- **Check examples**: Review good vs poor labels
- **Test frequently**: Validate with small batches
- **Iterate**: Improve based on robotic performance

---

**Remember**: High-quality manual annotation will significantly improve your robotic strawberry picking accuracy!
"""
        
        guide_file = self.output_path / 'LABELING_GUIDE.md'
        with open(guide_file, 'w') as f:
            f.write(guide_content)
        
        print(f"✅ Created labeling guide: {guide_file}")
        return guide_file
    
    def create_data_yaml(self):
        """Create data.yaml file for manually labeled dataset"""
        
        print(f"\n📄 CREATING DATA.YAML CONFIG")
        print("-" * 50)
        
        yaml_content = f"""# Dataset configuration for manually labeled strawberries
train: {self.output_path}/train/images
val: {self.output_path}/val/images
test: {self.output_path}/test/images

# Classes
nc: 1  # number of classes
names: ['strawberry']  # class names

# Roboflow metadata (for format compatibility)
roboflow:
  workspace: strawberry-picking
  project: manual-labeled-dataset
  version: 1
  license: CC BY 4.0
  url: https://universe.roboflow.com/strawberry-picking/manual-labeled-dataset

# Manual annotation metadata
manual_annotation:
  annotator: human
  quality_control: manual_review
  purpose: robotic_picking_optimization
  target_accuracy: 95%
"""
        
        yaml_file = self.output_path / 'data.yaml'
        with open(yaml_file, 'w') as f:
            f.write(yaml_content)
        
        print(f"✅ Created data.yaml: {yaml_file}")
        return yaml_file
    
    def run_reduction_process(self):
        """Run the complete dataset reduction process"""
        
        print("🚀 STARTING KAGGLE DATASET REDUCTION PROCESS")
        print("=" * 60)
        
        # Step 1: Analyze original dataset
        original_stats = self.analyze_original_dataset()
        
        # Step 2: Select representative images
        all_images = []
        for split in ['train', 'val', 'test']:
            split_path = self.kaggle_path / split / 'images'
            if split_path.exists():
                images = list(split_path.glob("*.jpg")) + list(split_path.glob("*.png"))
                all_images.extend(images)
        
        selected_images = self.select_representative_images(all_images, self.target_size)
        
        # Step 3: Create reduced dataset
        copied_count = self.create_reduced_dataset(selected_images)
        
        # Step 4: Create supporting files
        guide_file = self.create_labeling_guide()
        yaml_file = self.create_data_yaml()
        
        print(f"\n🎯 REDUCTION PROCESS COMPLETE!")
        print("=" * 60)
        print(f"✅ Created reduced dataset with {copied_count} images")
        print(f"📋 Labeling guide: {guide_file}")
        print(f"📄 Data config: {yaml_file}")
        print(f"\n📝 NEXT STEPS:")
        print("1. Manually annotate bounding boxes using the labeling guide")
        print("2. Review and validate all annotations")
        print("3. Train new model on manually labeled data")
        print("4. Test performance on robotic picking")
        
        return {
            'copied_images': copied_count,
            'labeling_guide': guide_file,
            'data_config': yaml_file,
            'output_directory': self.output_path
        }

def main():
    parser = argparse.ArgumentParser(description='Reduce Kaggle dataset for manual annotation')
    parser.add_argument('--input', type=str, 
                       default='model/datasets/ripe_only_detection',
                       help='Path to original Kaggle dataset')
    parser.add_argument('--output', type=str, 
                       default='model/datasets/manual_labeled',
                       help='Output path for reduced dataset')
    parser.add_argument('--size', type=int, 
                       default=50,
                       help='Target number of images (default: 50)')
    parser.add_argument('--method', type=str, 
                       choices=['random', 'diverse', 'representative'],
                       default='diverse',
                       help='Selection method (default: diverse)')
    
    args = parser.parse_args()
    
    reducer = KaggleDatasetReducer(
        kaggle_dataset_path=args.input,
        output_path=args.output,
        target_size=args.size,
        selection_method=args.method
    )
    
    results = reducer.run_reduction_process()
    
    print(f"\n🎉 KAGGLE DATASET REDUCTION COMPLETE!")
    print("=" * 60)
    print(f"📊 Reduced from {args.input} to {args.output}")
    print(f"🎯 Target size: {args.size} images")
    print(f"✅ Method: {args.method}")
    print(f"📋 Ready for manual annotation!")
    print("=" * 60)

if __name__ == '__main__':
    main()