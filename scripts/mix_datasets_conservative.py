#!/usr/bin/env python3
"""
PHASE 1 - CONSERVATIVE MIX: 50% Homemade + 50% Kaggle
Maintains excellent false positive elimination while adding dataset diversity
"""

import os
import shutil
import random
from pathlib import Path
from collections import defaultdict
import yaml

class DatasetMixer:
    def __init__(self, homemade_path, kaggle_path, output_path, mix_ratio=0.5):
        """
        Mix datasets conservatively to maintain false positive elimination
        
        Args:
            homemade_path: Path to homemade dataset (with negatives)
            kaggle_path: Path to Kaggle dataset (strawberries only)
            output_path: Output path for mixed dataset
            mix_ratio: Ratio of Kaggle data to include (0.5 = 50%)
        """
        self.homemade_path = Path(homemade_path)
        self.kaggle_path = Path(kaggle_path)
        self.output_path = Path(output_path)
        self.mix_ratio = mix_ratio
        
        # Create output directories
        self.output_path.mkdir(exist_ok=True)
        for split in ['train', 'valid', 'test']:
            (self.output_path / 'images' / split).mkdir(parents=True, exist_ok=True)
            (self.output_path / 'labels' / split).mkdir(parents=True, exist_ok=True)
    
    def count_images(self, dataset_path, split):
        """Count images in a dataset split"""
        # Try different possible directory structures
        image_dir = dataset_path / 'images' / split
        if not image_dir.exists():
            image_dir = dataset_path / split / 'images'
        
        if image_dir.exists():
            return len(list(image_dir.glob('*.jpg'))) + len(list(image_dir.glob('*.png')))
        return 0
    
    def get_image_label_pairs(self, dataset_path, split):
        """Get matching image-label pairs"""
        # Try different possible directory structures
        image_dir = dataset_path / 'images' / split
        label_dir = dataset_path / 'labels' / split
        
        # If the above doesn't exist, try the direct structure
        if not image_dir.exists():
            image_dir = dataset_path / split / 'images'
            label_dir = dataset_path / split / 'labels'
        
        pairs = []
        if image_dir.exists():
            for img_file in image_dir.glob('*.jpg'):
                label_file = label_dir / f"{img_file.stem}.txt"
                if label_file.exists():
                    pairs.append((img_file, label_file))
                else:
                    # Handle empty labels (negatives)
                    pairs.append((img_file, None))
            
            for img_file in image_dir.glob('*.png'):
                label_file = label_dir / f"{img_file.stem}.txt"
                if label_file.exists():
                    pairs.append((img_file, label_file))
                else:
                    pairs.append((img_file, None))
        
        return pairs
    
    def copy_with_new_name(self, src_img, src_label, dst_img_path, dst_label_path, prefix):
        """Copy files with new names to avoid conflicts"""
        # Copy image
        shutil.copy2(src_img, dst_img_path)
        
        # Copy or create label
        if src_label and src_label.exists():
            shutil.copy2(src_label, dst_label_path)
        else:
            # Create empty label file for negatives
            dst_label_path.touch()
    
    def mix_dataset_split(self, split):
        """Mix a specific dataset split (train/valid/test)"""
        print(f"\n🔄 Processing {split} split...")
        
        # Get pairs from both datasets
        homemade_pairs = self.get_image_label_pairs(self.homemade_path, split)
        kaggle_pairs = self.get_image_label_pairs(self.kaggle_path, split)
        
        print(f"   Homemade {split}: {len(homemade_pairs)} images")
        print(f"   Kaggle {split}: {len(kaggle_pairs)} images")
        
        # Calculate how many Kaggle images to include
        target_kaggle_count = int(len(kaggle_pairs) * self.mix_ratio)
        
        # Randomly sample Kaggle images (but maintain representativeness)
        if len(kaggle_pairs) > target_kaggle_count:
            # Stratified sampling: try to maintain similar distribution
            kaggle_sample = random.sample(kaggle_pairs, target_kaggle_count)
        else:
            kaggle_sample = kaggle_pairs
        
        print(f"   Selected {len(kaggle_sample)} Kaggle images for mixing")
        
        # Combine datasets
        all_pairs = homemade_pairs + kaggle_sample
        
        # Shuffle to mix them well
        random.shuffle(all_pairs)
        
        # Copy files to output directory
        for i, (img_path, label_path) in enumerate(all_pairs):
            # Generate new name to avoid conflicts
            new_name = f"mixed_{split}_{i:06d}"
            
            dst_img = self.output_path / 'images' / split / f"{new_name}.jpg"
            dst_label = self.output_path / 'labels' / split / f"{new_name}.txt"
            
            # Copy with new name
            self.copy_with_new_name(img_path, label_path, dst_img, dst_label, split)
        
        print(f"   Created {len(all_pairs)} mixed images for {split}")
        return len(all_pairs)
    
    def create_data_yaml(self):
        """Create data.yaml for the mixed dataset"""
        data_config = {
            'path': str(self.output_path.absolute()),
            'train': 'train/images',
            'val': 'valid/images', 
            'test': 'test/images',
            'nc': 1,
            'names': ['strawberry']
        }
        
        yaml_path = self.output_path / 'data.yaml'
        with open(yaml_path, 'w') as f:
            yaml.dump(data_config, f, default_flow_style=False)
        
        print(f"✅ Created data.yaml: {yaml_path}")
    
    def analyze_dataset_composition(self):
        """Analyze the composition of the mixed dataset"""
        print("\n📊 Dataset Composition Analysis:")
        print("=" * 50)
        
        total_stats = defaultdict(int)
        
        for split in ['train', 'valid', 'test']:
            image_dir = self.output_path / 'images' / split
            label_dir = self.output_path / 'labels' / split
            
            if not image_dir.exists():
                continue
            
            strawberry_count = 0
            empty_count = 0
            
            # Count images and check for corresponding labels
            for img_file in image_dir.glob('*.jpg'):
                label_file = label_dir / f"{img_file.stem}.txt"
                
                if label_file.exists():
                    # Check if label file has content
                    if label_file.stat().st_size == 0:
                        empty_count += 1  # Negative example (empty label)
                    else:
                        # Check if it's actually a strawberry detection
                        with open(label_file, 'r') as f:
                            content = f.read().strip()
                            if content:
                                strawberry_count += 1
                            else:
                                empty_count += 1
                else:
                    # No label file = negative example
                    empty_count += 1
            
            total_images = strawberry_count + empty_count
            total_stats[f'{split}_total'] = total_images
            total_stats[f'{split}_strawberries'] = strawberry_count
            total_stats[f'{split}_negatives'] = empty_count
            
            print(f"{split.capitalize()}:")
            print(f"  Total: {total_images}")
            print(f"  Strawberries: {strawberry_count}")
            print(f"  Negatives: {empty_count}")
            if total_images > 0:
                print(f"  Negative ratio: {empty_count/total_images*100:.1f}%")
            print()
        
        # Overall stats
        total_images = sum(v for k, v in total_stats.items() if k.endswith('_total'))
        total_strawberries = sum(v for k, v in total_stats.items() if k.endswith('_strawberries'))
        total_negatives = sum(v for k, v in total_stats.items() if k.endswith('_negatives'))
        
        print("Overall:")
        print(f"  Total images: {total_images}")
        print(f"  Total strawberries: {total_strawberries}")
        print(f"  Total negatives: {total_negatives}")
        if total_images > 0:
            print(f"  Overall negative ratio: {total_negatives/total_images*100:.1f}%")
        
        return total_stats
    
    def mix_datasets(self):
        """Main mixing function"""
        print("🍓 PHASE 1 - CONSERVATIVE DATASET MIXING")
        print("=" * 60)
        print(f"Homemade dataset: {self.homemade_path}")
        print(f"Kaggle dataset: {self.kaggle_path}")
        print(f"Output path: {self.output_path}")
        print(f"Mix ratio: {self.mix_ratio*100}% Kaggle data")
        print()
        
        # Process each split
        total_images = 0
        for split in ['train', 'valid', 'test']:
            count = self.mix_dataset_split(split)
            total_images += count
        
        # Create data.yaml
        self.create_data_yaml()
        
        # Analyze composition
        stats = self.analyze_dataset_composition()
        
        print(f"\n✅ Successfully created mixed dataset with {total_images} total images!")
        print(f"📁 Output directory: {self.output_path}")
        
        return stats

def main():
    """Main function for conservative dataset mixing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Mix homemade and Kaggle datasets conservatively')
    parser.add_argument('--homemade', type=str, default='model/dataset_homemade_labeled',
                       help='Path to homemade dataset')
    parser.add_argument('--kaggle', type=str, default='model/dataset_strawberry_kaggle',
                       help='Path to Kaggle dataset')
    parser.add_argument('--output', type=str, default='model/dataset_mixed_conservative',
                       help='Output path for mixed dataset')
    parser.add_argument('--ratio', type=float, default=0.5,
                       help='Ratio of Kaggle data to include (0.5 = 50%)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Set random seed for reproducibility
    random.seed(args.seed)
    
    # Create mixer and run
    mixer = DatasetMixer(
        homemade_path=args.homemade,
        kaggle_path=args.kaggle,
        output_path=args.output,
        mix_ratio=args.ratio
    )
    
    stats = mixer.mix_datasets()
    
    print("\n🎯 Next Steps:")
    print("1. Train model on mixed dataset:")
    print(f"   python scripts/train_yolov8n_no_early_stop.py --data {args.output}/data.yaml")
    print("2. Test performance:")
    print(f"   python scripts/test_homemade_model.py --data {args.output}/data.yaml")
    print("3. Compare with baseline:")
    print("   python scripts/test_and_compare_models.py")

if __name__ == '__main__':
    main()