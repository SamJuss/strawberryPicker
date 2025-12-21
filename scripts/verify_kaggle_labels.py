#!/usr/bin/env python3
"""
Verify Kaggle dataset bounding boxes by visualizing labels on images
"""

import cv2
import numpy as np
from pathlib import Path
import random
import argparse

def load_yolo_label(label_path, img_width, img_height):
    """Load YOLO format label and convert to pixel coordinates"""
    boxes = []
    if not label_path.exists():
        return boxes
    
    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                
                # Convert from normalized to pixel coordinates
                x1 = int((x_center - width/2) * img_width)
                y1 = int((y_center - height/2) * img_height)
                x2 = int((x_center + width/2) * img_width)
                y2 = int((y_center + height/2) * img_height)
                
                boxes.append({
                    'class_id': class_id,
                    'bbox': [x1, y1, x2, y2],
                    'confidence': 1.0  # Ground truth
                })
    return boxes

def verify_kaggle_labels(data_dir='model/datasets/ripe_only_detection', 
                        split='train', 
                        num_samples=10,
                        output_dir=None):
    """Verify Kaggle dataset labels by visualizing them"""
    
    data_path = Path(data_dir)
    images_dir = data_path / split / 'images'
    labels_dir = data_path / split / 'labels'
    
    if not images_dir.exists() or not labels_dir.exists():
        print(f"❌ Dataset directories not found: {images_dir} or {labels_dir}")
        return
    
    # Get image files
    image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
    if not image_files:
        print(f"❌ No images found in {images_dir}")
        return
    
    print(f"🔍 Verifying Kaggle {split} dataset labels")
    print(f"📁 Images: {len(image_files)} files")
    print(f"📁 Labels: {len(list(labels_dir.glob('*.txt')))} files")
    
    # Create output directory
    if output_dir is None:
        output_dir = Path(f"kaggle_label_verification_{split}")
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Sample random images for verification
    sample_files = random.sample(image_files, min(num_samples, len(image_files)))
    
    verification_results = {
        'total_images': len(sample_files),
        'images_with_labels': 0,
        'total_boxes': 0,
        'avg_boxes_per_image': 0,
        'issues_found': []
    }
    
    for i, img_path in enumerate(sample_files, 1):
        print(f"\n📸 Verifying image {i}/{len(sample_files)}: {img_path.name}")
        
        # Load image
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"  ❌ Could not load image: {img_path.name}")
            verification_results['issues_found'].append(f"Could not load: {img_path.name}")
            continue
            
        img_height, img_width = img.shape[:2]
        
        # Load corresponding label
        label_path = labels_dir / f"{img_path.stem}.txt"
        boxes = load_yolo_label(label_path, img_width, img_height)
        
        if boxes:
            verification_results['images_with_labels'] += 1
            verification_results['total_boxes'] += len(boxes)
            print(f"  ✅ Found {len(boxes)} bounding boxes")
            
            # Draw bounding boxes
            for box in boxes:
                x1, y1, x2, y2 = box['bbox']
                
                # Validate box coordinates
                if x1 < 0 or y1 < 0 or x2 > img_width or y2 > img_height:
                    print(f"    ⚠️  Box coordinates out of bounds: {box['bbox']}")
                    verification_results['issues_found'].append(f"Out of bounds box in {img_path.name}: {box['bbox']}")
                
                if x2 <= x1 or y2 <= y1:
                    print(f"    ⚠️  Invalid box dimensions: {box['bbox']}")
                    verification_results['issues_found'].append(f"Invalid dimensions in {img_path.name}: {box['bbox']}")
                
                # Draw box
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, 'strawberry', (x1, y1-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        else:
            print(f"  ℹ️  No labels found for this image")
        
        # Save visualization
        output_path = output_dir / f"verified_{img_path.name}"
        cv2.imwrite(str(output_path), img)
        print(f"  💾 Saved visualization: {output_path.name}")
    
    # Print summary
    print(f"\n" + "="*60)
    print("🔍 VERIFICATION SUMMARY")
    print("="*60)
    print(f"Images verified: {verification_results['total_images']}")
    print(f"Images with labels: {verification_results['images_with_labels']}")
    print(f"Total bounding boxes: {verification_results['total_boxes']}")
    
    if verification_results['total_images'] > 0:
        avg_boxes = verification_results['total_boxes'] / verification_results['images_with_labels'] if verification_results['images_with_labels'] > 0 else 0
        print(f"Average boxes per labeled image: {avg_boxes:.1f}")
        print(f"Label coverage: {verification_results['images_with_labels']/verification_results['total_images']*100:.1f}%")
    
    if verification_results['issues_found']:
        print(f"\n⚠️  Issues found: {len(verification_results['issues_found'])}")
        for issue in verification_results['issues_found'][:5]:  # Show first 5
            print(f"  - {issue}")
        if len(verification_results['issues_found']) > 5:
            print(f"  ... and {len(verification_results['issues_found'])-5} more")
    else:
        print("\n✅ No issues found - labels look good!")
    
    print(f"\n📁 Visualizations saved to: {output_dir}")
    
    return verification_results

def main():
    parser = argparse.ArgumentParser(description='Verify Kaggle dataset labels')
    parser.add_argument('--data', type=str, default='model/datasets/ripe_only_detection',
                       help='Path to dataset directory')
    parser.add_argument('--split', type=str, default='train',
                       choices=['train', 'val', 'test'],
                       help='Dataset split to verify')
    parser.add_argument('--num', type=int, default=10,
                       help='Number of images to verify')
    parser.add_argument('--output', type=str, default=None,
                       help='Output directory for visualizations')
    
    args = parser.parse_args()
    
    verify_kaggle_labels(
        data_dir=args.data,
        split=args.split,
        num_samples=args.num,
        output_dir=args.output
    )

if __name__ == '__main__':
    main()