#!/usr/bin/env python3
"""
PHASE 1 - CONSERVATIVE MIX WITH NEGATIVES: 50% Homemade + 50% Kaggle
Includes synthetic negative examples to maintain false positive elimination
"""

import os
import shutil
import random
from pathlib import Path
from collections import defaultdict
import yaml

class DatasetMixerWithNegatives:
    def __init__(self, homemade_path, kaggle_path, output_path, mix_ratio=0.5):
        """
        Mix datasets including synthetic negative examples
        
        Args:
            homemade_path: Path to homemade dataset (with synthetic negatives)
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
    
    def get_synthetic_negatives(self):
        """Get all synthetic negative images from homemade dataset"""
        synthetic_images = []
        
        # Look for synthetic images in the images directory
        images_dir = self.homemade_path / 'images'
        if images_dir.exists():
            for img_file in images_dir.glob('synthetic_*.jpg'):
                synthetic_images.append(img_file)
        
        print(f"Found {len(synthetic_images)} synthetic negative images")
        return synthetic_images
    
    def get_split_pairs(self, dataset_path, split):
        """Get image-label pairs for a specific split"""
        image_dir = dataset_path / split / 'images'
        label_dir = dataset_path / split / 'labels'
        
        pairs = []
        if image_dir.exists():
            for img_file in image_dir.glob('*.jpg'):
                label_file = label_dir / f"{img_file.stem}.txt"
                if label_file.exists():
                    pairs.append((img_file, label_file, 'strawberry'))
                else:
                    # No label file = negative example
                    pairs.append((img_file, None, 'negative'))
            
            for img_file in image_dir.glob('*.png'):
                label_file = label_dir / f"{img_file.stem}.txt"
                if label_file.exists():
                    pairs.append((img_file, label_file, 'strawberry'))
                else:
                    pairs.append((img_file, None, 'negative'))
        
        return pairs
    
    def redistribute_synthetic_negatives(self, synthetic_images):
        """Redistribute synthetic negatives evenly across splits"""
        random.shuffle(synthetic_images)
        
        # Split roughly 70/15/15 for train/valid/test
        total = len(synthetic_images)
        train_count = int(total * 0.7)
        valid_count = int(total * 0.15)
        
        train_negs = synthetic_images[:train_count]
        valid_negs = synthetic_images[train_count:train_count + valid_count]
        test_negs = synthetic_images[train_count + valid_count:]
        
        return {
            'train': [(img, None, 'synthetic_negative') for img in train_negs],
            'valid': [(img, None, 'synthetic_negative') for img in valid_negs],
            'test': [(img, None, 'synthetic_negative') for img in test_negs]
        }
    
    def mix_dataset_split(self, split, synthetic_negatives):
        """Mix a specific dataset split with synthetic negatives"""
        print(f"\n🔄 Processing {split} split...")
        
        # Get pairs from both datasets
        homemade_pairs = self.get_split_pairs(self.homemade_path, split)
        kaggle_pairs = self.get_split_pairs(self.kaggle_path, split)
        
        print(f"   Homemade {split}: {len(homemade_pairs)} images")
        print(f"   Kaggle {split}: {len(kaggle_pairs)} images")
        print(f"   Synthetic negatives {split}: {len(synthetic_negatives[split])} images")
        
        # Calculate how many Kaggle images to include
        target_kaggle_count = int(len(kaggle_pairs) * self.mix_ratio)
        
        # Randomly sample Kaggle images
        if len(kaggle_pairs) > target_kaggle_count:
            kaggle_sample = random.sample(kaggle_pairs, target_kaggle_count)
        else:
            kaggle_sample = kaggle_pairs
        
        print(f"   Selected {len(kaggle_sample)} Kaggle images for mixing")
        
        # Combine datasets: homemade + sampled kaggle + synthetic negatives
        all_pairs = homemade_pairs + kaggle_sample + synthetic_negatives[split]
        
        # Shuffle to mix them well
        random.shuffle(all_pairs)
        
        # Copy files to output directory
        for i, (img_path, label_path, img_type) in enumerate(all_pairs):
            # Generate new name to avoid conflicts
            new_name = f"mixed_{split}_{i:06d}"
            
            dst_img = self.output_path / 'images' / split / f"{new_name}.jpg"
            dst_label = self.output_path / 'labels' / split / f"{new_name}.txt"
            
            # Copy image
            shutil.copy2(img_path, dst_img)
            
            # Handle label (create empty file for negatives)
            if label_path and label_path.exists():
                shutil.copy2(label_path, dst_label)
            else:
                # Create empty label file for negatives
                dst_label.touch()
        
        print(f"   Created {len(all_pairs)} mixed images for {split}")
        
        # Return statistics
        strawberry_count = sum(1 for _, label, img_type in all_pairs if img_type in ['strawberry'])
        negative_count = sum(1 for _, label, img_type in all_pairs if img_type in ['negative', 'synthetic_negative'])
        
        return len(all_pairs), strawberry_count, negative_count
    
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
            negative_count = 0
            
            # Count images and check for corresponding labels
            for img_file in image_dir.glob('*.jpg'):
                label_file = label_dir / f"{img_file.stem}.txt"
                
                if label_file.exists() and label_file.stat().st_size > 0:
                    # Has content = strawberry detection
                    strawberry_count += 1
                else:
                    # Empty or missing = negative example
                    negative_count += 1
            
            total_images = strawberry_count + negative_count
            total_stats[f'{split}_total'] = total_images
            total_stats[f'{split}_strawberries'] = strawberry_count
            total_stats[f'{split}_negatives'] = negative_count
            
            print(f"{split.capitalize()}:")
            print(f"  Total: {total_images}")
            print(f"  Strawberries: {strawberry_count}")
            print(f"  Negatives: {negative_count}")
            if total_images > 0:
                print(f"  Negative ratio: {negative_count/total_images*100:.1f}%")
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
        print("🍓 PHASE 1 - CONSERVATIVE DATASET MIXING WITH NEGATIVES")
        print("=" * 70)
        print(f"Homemade dataset: {self.homemade_path}")
        print(f"Kaggle dataset: {self.kaggle_path}")
        print(f"Output path: {self.output_path}")
        print(f"Mix ratio: {self.mix_ratio*100}% Kaggle data")
        print()
        
        # Get synthetic negatives
        synthetic_images = self.get_synthetic_negatives()
        synthetic_negatives = self.redistribute_synthetic_negatives(synthetic_images)
        
        # Process each split
        total_images = 0
        total_strawberries = 0
        total_negatives = 0
        
        for split in ['train', 'valid', 'test']:
            count, strawberries, negatives = self.mix_dataset_split(split, synthetic_negatives)
            total_images += count
            total_strawberries += strawberries
            total_negatives += negatives
        
        # Create data.yaml
        self.create_data_yaml()
        
        # Analyze composition
        stats = self.analyze_dataset_composition()
        
        print(f"\n✅ Successfully created mixed dataset with {total_images} total images!")
        print(f"📁 Output directory: {self.output_path}")
        print(f"📊 Composition: {total_strawberries} strawberries, {total_negatives} negatives")
        
        return stats

def main():
    """Main function for conservative dataset mixing with negatives"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Mix datasets including synthetic negative examples')
    parser.add_argument('--homemade', type=str, default='model/dataset_homemade_labeled',
                       help='Path to homemade dataset with synthetic negatives')
    parser.add_argument('--kaggle', type=str, default='model/dataset_strawberry_kaggle',
                       help='Path to Kaggle dataset')
    parser.add_argument('--output', type=str, default='model/dataset_mixed_conservative_v2',
                       help='Output path for mixed dataset')
    parser.add_argument('--ratio', type=float, default=0.5,
                       help='Ratio of Kaggle data to include (0.5 = 50%)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Set random seed for reproducibility
    random.seed(args.seed)
    
    # Create mixer and run
    mixer = DatasetMixerWithNegatives(
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