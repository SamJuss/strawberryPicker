#!/usr/bin/env python3
"""
Fix the ripe-only dataset by copying validation images from 'valid' to 'val'.
"""

import os
import shutil
from pathlib import Path

def copy_validation_images():
    source_root = Path('model/datasets/ripeness_detection')
    target_root = Path('model/datasets/ripe_only_detection')
    
    # Copy validation images
    source_val_img = source_root / 'valid' / 'images'
    target_val_img = target_root / 'val' / 'images'
    target_val_img.mkdir(parents=True, exist_ok=True)
    
    source_val_labels = source_root / 'valid' / 'labels'
    target_val_labels = target_root / 'val' / 'labels'
    target_val_labels.mkdir(parents=True, exist_ok=True)
    
    # Copy images
    for img_path in source_val_img.glob('*.jpg'):
        shutil.copy(img_path, target_val_img / img_path.name)
    
    # Filter labels for ripe only (class 1 -> 0)
    for label_path in source_val_labels.glob('*.txt'):
        with open(label_path, 'r') as f:
            lines = f.readlines()
        
        ripe_lines = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 5:
                cls = int(parts[0])
                if cls == 1:  # ripe
                    parts[0] = '0'
                    ripe_lines.append(' '.join(parts))
        
        # Write filtered labels
        if ripe_lines:
            with open(target_val_labels / label_path.name, 'w') as f:
                f.write('\n'.join(ripe_lines))
        else:
            # Create empty label file
            open(target_val_labels / label_path.name, 'w').close()
    
    print(f"Copied {len(list(source_val_img.glob('*.jpg')))} validation images")
    print(f"Processed {len(list(source_val_labels.glob('*.txt')))} label files")

def count_dataset():
    target_root = Path('model/datasets/ripe_only_detection')
    splits = ['train', 'val', 'test']
    
    for split in splits:
        img_dir = target_root / split / 'images'
        label_dir = target_root / split / 'labels'
        
        if not img_dir.exists():
            print(f"{split}: images directory missing")
            continue
        
        images = list(img_dir.glob('*.jpg'))
        labels = list(label_dir.glob('*.txt'))
        
        # Count annotations
        total_annotations = 0
        for lbl in labels:
            with open(lbl, 'r') as f:
                lines = f.readlines()
                total_annotations += len([l for l in lines if l.strip()])
        
        print(f"{split}: {len(images)} images, {len(labels)} label files, {total_annotations} ripe annotations")

if __name__ == '__main__':
    copy_validation_images()
    count_dataset()