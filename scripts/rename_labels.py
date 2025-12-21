#!/usr/bin/env python3
"""
Rename label files from .jpg.txt to .txt format
"""

import os
from pathlib import Path

def rename_labels():
    src_dir = Path('model/dataset_homemade')
    
    # Find all .jpg.txt files
    label_files = list(src_dir.glob('*.jpg.txt'))
    
    print(f"Found {len(label_files)} label files to rename")
    
    renamed_count = 0
    for label_file in label_files:
        # New name: remove .jpg before .txt
        new_name = label_file.name.replace('.jpg.txt', '.txt')
        new_path = label_file.parent / new_name
        
        # Rename
        label_file.rename(new_path)
        renamed_count += 1
    
    print(f"Successfully renamed {renamed_count} label files")

if __name__ == '__main__':
    rename_labels()