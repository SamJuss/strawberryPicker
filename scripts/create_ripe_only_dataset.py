#!/usr/bin/env python3
"""
Create a single-class dataset (ripe only) from the ripeness detection dataset.
"""

import os
import shutil
from pathlib import Path
import yaml

def filter_ripe_only(source_root, target_root):
    """
    Copy images and filter labels to only include ripe (class 1) and remap to class 0.
    """
    splits = ['train', 'val', 'test']
    
    for split in splits:
        source_img_dir = Path(source_root) / split / 'images'
        source_label_dir = Path(source_root) / split / 'labels'
        target_img_dir = Path(target_root) / split / 'images'
        target_label_dir = Path(target_root) / split / 'labels'
        
        target_img_dir.mkdir(parents=True, exist_ok=True)
        target_label_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all image files (assuming .jpg)
        image_files = list(source_img_dir.glob('*.jpg'))
        print(f"{split}: Found {len(image_files)} images")
        
        ripe_count = 0
        total_annotations = 0
        
        for img_path in image_files:
            label_path = source_label_dir / (img_path.stem + '.txt')
            
            # Copy image
            shutil.copy(img_path, target_img_dir / img_path.name)
            
            # Process label file if exists
            if label_path.exists():
                with open(label_path, 'r') as f:
                    lines = f.readlines()
                
                ripe_lines = []
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        cls = int(parts[0])
                        total_annotations += 1
                        if cls == 1:  # ripe class
                            # Change class to 0 (single class)
                            parts[0] = '0'
                            ripe_lines.append(' '.join(parts))
                            ripe_count += 1
                
                # Write filtered labels
                if ripe_lines:
                    with open(target_label_dir / label_path.name, 'w') as f:
                        f.write('\n'.join(ripe_lines))
            else:
                # No label file, create empty
                open(target_label_dir / (img_path.stem + '.txt'), 'w').close()
        
        print(f"{split}: Kept {ripe_count} ripe annotations out of {total_annotations} total annotations")

def create_data_yaml(target_root, dataset_name="ripe_only_detection"):
    """
    Create data.yaml for the single-class dataset.
    """
    data = {
        'train': 'train/images',
        'val': 'val/images',
        'test': 'test/images',
        'nc': 1,
        'names': ['ripe'],
        'roboflow': {
            'workspace': 'strawberry-ripeness-detection-p8bvl',
            'project': 'strawberry-ripeness-detection-48rpf',
            'version': 6,
            'license': 'CC BY 4.0',
            'url': 'https://universe.roboflow.com/strawberry-ripeness-detection-p8bvl/strawberry-ripeness-detection-48rpf/dataset/6'
        }
    }
    
    yaml_path = Path(target_root) / 'data.yaml'
    with open(yaml_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
    
    print(f"Created data.yaml at {yaml_path}")
    print(f"Classes: {data['names']}")
    print(f"Number of classes: {data['nc']}")

def main():
    source_dataset = 'model/datasets/ripeness_detection'
    target_dataset = 'model/datasets/ripe_only_detection'
    
    print(f"Source dataset: {source_dataset}")
    print(f"Target dataset: {target_dataset}")
    
    # Check if source exists
    if not os.path.exists(source_dataset):
        print(f"Error: Source dataset not found at {source_dataset}")
        return
    
    # Filter and copy
    filter_ripe_only(source_dataset, target_dataset)
    
    # Create data.yaml
    create_data_yaml(target_dataset)
    
    print("\nDataset preparation complete.")

if __name__ == '__main__':
    main()