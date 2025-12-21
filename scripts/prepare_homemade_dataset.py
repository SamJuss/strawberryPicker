#!/usr/bin/env python3
"""
Prepare the homemade dataset for training by splitting into train/val/test
and creating the data.yaml file.
"""

import os
import random
import shutil
from pathlib import Path

def prepare_dataset():
    # Paths
    src_dir = Path('model/dataset_homemade')
    labeled_src_dir = Path('model/dataset_homemade_labeled')
    dst_dir = Path('model/dataset_homemade_labeled')
    
    # Get strawberry images from original directory
    strawberry_images = sorted([f for f in src_dir.glob('WIN_*_Pro.jpg')
                               if not f.name.endswith(':Zone.Identifier')])
    
    # Get negative examples from labeled directory (they're already there)
    # Find all images and check if their labels are empty
    all_images_in_labeled = [f for f in labeled_src_dir.glob('images/*.jpg')
                            if not f.name.endswith(':Zone.Identifier')]

    negative_images = []
    for img_file in all_images_in_labeled:
        label_file = labeled_src_dir / 'labels' / img_file.with_suffix('.txt').name
        if label_file.exists():
            with open(label_file, 'r') as f:
                content = f.read().strip()
            if not content:  # Empty label = negative example
                negative_images.append(img_file)

    negative_images = sorted(negative_images)
    
    # Get corresponding label files for strawberries
    labeled_images = []
    for img_file in strawberry_images:
        label_file = img_file.with_suffix('.txt')
        if label_file.exists() and label_file.stat().st_size > 0:
            labeled_images.append(img_file)
    
    # Add negative examples (they're already in the labeled directory)
    all_images = labeled_images + negative_images
    
    print(f"Found {len(strawberry_images)} strawberry images")
    print(f"Found {len(labeled_images)} labeled strawberry images")
    print(f"Found {len(negative_images)} negative examples")
    print(f"Total images for dataset: {len(all_images)}")
    
    if len(labeled_images) < 3:
        print("Error: Need at least 3 labeled images to split dataset")
        return False
    
    # Split dataset
    # For small datasets, use: 70% train, 20% val, 10% test
    random.seed(42)  # For reproducibility
    random.shuffle(labeled_images)
    
    n_total = len(labeled_images)
    n_train = int(0.7 * n_total)
    n_val = int(0.2 * n_total)
    n_test = n_total - n_train - n_val
    
    train_images = labeled_images[:n_train]
    val_images = labeled_images[n_train:n_train + n_val]
    test_images = labeled_images[n_train + n_val:]
    
    print(f"Split: {len(train_images)} train, {len(val_images)} val, {len(test_images)} test")
    
    # Copy files to respective directories
    splits = {
        'train': train_images,
        'valid': val_images,
        'test': test_images
    }
    
    for split_name, images in splits.items():
        img_dir = dst_dir / split_name / 'images'
        lbl_dir = dst_dir / split_name / 'labels'
        
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)
        
        for img_file in images:
            # Copy image
            shutil.copy2(img_file, img_dir / img_file.name)
            
            # Copy label
            label_file = img_file.with_suffix('.txt')
            if label_file.exists():
                shutil.copy2(label_file, lbl_dir / label_file.name)
    
    # Create data.yaml
    data_yaml = f"""path: /home/user/machine-learning/GitHubRepos/strawberryPicker/model/dataset_homemade_labeled
train: train/images
val: valid/images
test: test/images

nc: 1
names: ['strawberry']
"""
    
    yaml_path = dst_dir / 'data.yaml'
    with open(yaml_path, 'w') as f:
        f.write(data_yaml)
    
    print(f"\nDataset prepared successfully!")
    print(f"Train images: {len(train_images)}")
    print(f"Val images: {len(val_images)}")
    print(f"Test images: {len(test_images)}")
    print(f"Data config: {yaml_path}")
    
    return True

if __name__ == '__main__':
    prepare_dataset()