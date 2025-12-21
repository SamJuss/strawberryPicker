#!/usr/bin/env python3
"""
Fix dataset to include negative examples in training
"""

import shutil
from pathlib import Path
import sys

def fix_dataset_with_negatives():
    """Copy negative examples to labeled dataset and re-prepare"""
    
    print("="*70)
    print("FIXING DATASET TO INCLUDE NEGATIVE EXAMPLES")
    print("="*70)
    
    # Paths
    homemade_dir = Path('model/dataset_homemade')
    labeled_dir = Path('model/dataset_homemade_labeled')
    negative_dir = labeled_dir / 'negative_examples'
    
    # Create negative examples directory
    negative_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {negative_dir}")
    
    # Find and copy negative examples
    negative_count = 0
    print("\nScanning for negative examples...")

    # Find all .txt files and check if they're empty (negative examples)
    for txt_path in homemade_dir.glob('*.txt'):
        with open(txt_path, 'r') as f:
            content = f.read().strip()

        # If file is empty (negative example)
        if not content:
            # Find corresponding image file
            img_path = txt_path.with_suffix('.jpg')
            if not img_path.exists():
                # Try other common extensions
                for ext in ['.jpeg', '.png', '.bmp']:
                    alt_img_path = txt_path.with_suffix(ext)
                    if alt_img_path.exists():
                        img_path = alt_img_path
                        break

            if img_path.exists():
                # Copy image
                dest_img = negative_dir / img_path.name
                shutil.copy2(img_path, dest_img)

                # Copy empty label file
                dest_txt = negative_dir / txt_path.name
                shutil.copy2(txt_path, dest_txt)

                negative_count += 1
                print(f"  Copied: {img_path.name}")
            else:
                print(f"  Warning: No image found for {txt_path.name}")

    # Also scan synthetic negative examples from subdirectories
    neg_examples_dir = homemade_dir / 'negative_examples'
    if neg_examples_dir.exists():
        print(f"\nScanning synthetic negatives in {neg_examples_dir}...")
        for category_dir in neg_examples_dir.iterdir():
            if category_dir.is_dir():
                print(f"  Processing category: {category_dir.name}")
                for img_path in category_dir.glob('*.jpg'):
                    txt_path = img_path.with_suffix('.txt')
                    if txt_path.exists():
                        # Copy image
                        dest_img = negative_dir / img_path.name
                        shutil.copy2(img_path, dest_img)

                        # Copy label file
                        dest_txt = negative_dir / txt_path.name
                        shutil.copy2(txt_path, dest_txt)

                        negative_count += 1
                        print(f"    Copied synthetic: {img_path.name}")

    print(f"\nCopied {negative_count} negative examples")
    
    # Verify the negative examples are now in the labeled dataset
    print("\nVerifying negative examples in labeled dataset...")
    
    # Count total images in labeled dataset
    total_images_before = len(list(labeled_dir.glob('*.jpg')))
    total_images_after = total_images_before + negative_count
    
    print(f"Total images before: {total_images_before}")
    print(f"Total images after: {total_images_after}")
    
    # Check if negative examples are in the images directory
    images_dir = labeled_dir / 'images'
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Move all images to images directory (if not already there)
    for img_path in labeled_dir.glob('WIN_*_Pro.jpg'):
        if img_path.parent == labeled_dir:  # Only move if in root
            dest = images_dir / img_path.name
            img_path.rename(dest)
            print(f"  Moved {img_path.name} to images/")

    # Move ALL negative examples to images directory (including synthetic ones)
    for img_path in negative_dir.glob('*.jpg'):
        dest = images_dir / img_path.name
        img_path.rename(dest)
        print(f"  Moved negative example {img_path.name} to images/")

    # Move label files similarly
    labels_dir = labeled_dir / 'labels'
    labels_dir.mkdir(parents=True, exist_ok=True)

    for txt_path in labeled_dir.glob('WIN_*_Pro.txt'):
        if txt_path.parent == labeled_dir:  # Only move if in root
            dest = labels_dir / txt_path.name
            txt_path.rename(dest)
            print(f"  Moved {txt_path.name} to labels/")

    # Move ALL negative label files
    for txt_path in negative_dir.glob('*.txt'):
        dest = labels_dir / txt_path.name
        txt_path.rename(dest)
        print(f"  Moved negative label {txt_path.name} to labels/")
    
    # Clean up empty negative_examples directory
    if negative_dir.exists() and not any(negative_dir.iterdir()):
        negative_dir.rmdir()
        print(f"\nCleaned up empty directory: {negative_dir}")
    
    print("\n" + "="*70)
    print("DATASET FIX COMPLETE!")
    print("="*70)
    print(f"Negative examples copied: {negative_count}")
    print(f"Total images in dataset: {total_images_after}")
    print("\nNext steps:")
    print("1. Run: python3 scripts/prepare_homemade_dataset.py")
    print("2. Verify negative examples are included in the split")
    print("3. Retrain model: python3 scripts/train_improved_model.py")
    print("="*70)

if __name__ == '__main__':
    fix_dataset_with_negatives()