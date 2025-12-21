#!/usr/bin/env python3
"""
Test the improved model on negative examples (body parts, red objects)
"""

from ultralytics import YOLO
from pathlib import Path
import sys

def test_negative_examples():
    """Test both old and new models on negative examples"""
    
    # Model paths
    old_model_path = 'model/detection/homemade_yolov8n_100epochs_expanded/weights/best.pt'
    new_model_path = 'model/detection/homemade_yolov8n_v2_negatives2/weights/best.pt'
    
    # Load models
    print("="*70)
    print("TESTING MODELS ON NEGATIVE EXAMPLES")
    print("="*70)
    print(f"Old model: {old_model_path}")
    print(f"New model: {new_model_path}")
    print("="*70)
    
    old_model = YOLO(old_model_path)
    new_model = YOLO(new_model_path)
    
    # Find negative examples (images with empty label files)
    homemade_dir = Path('model/dataset_homemade')
    negative_images = []
    
    for img_path in homemade_dir.glob('*.jpg'):
        txt_path = img_path.with_suffix('.txt')
        if txt_path.exists():
            with open(txt_path, 'r') as f:
                content = f.read().strip()
                if not content:  # Empty file = negative example
                    negative_images.append(img_path)
    
    if not negative_images:
        print("No negative examples found!")
        print("Looking for images with 'negative', 'finger', 'hand', 'arm', 'red' in filename...")
        
        # Alternative: look for images with specific names
        for pattern in ['*negative*', '*finger*', '*hand*', '*arm*', '*red*', '*body*']:
            negative_images.extend(homemade_dir.glob(pattern))
        
        if not negative_images:
            print("Still no negative examples found!")
            return
    
    print(f"\nFound {len(negative_images)} negative example images")
    print("Testing with conf=0.25, iou=0.7")
    print("-"*70)
    
    # Statistics
    old_false_positives = 0
    new_false_positives = 0
    images_with_improvement = 0
    
    for i, img_path in enumerate(negative_images):
        print(f"\n{i+1}. Testing: {img_path.name}")
        
        # Test old model
        old_results = old_model(img_path, conf=0.25, iou=0.7)
        old_result = old_results[0]
        old_detections = len(old_result.boxes)
        old_false_positives += old_detections
        
        # Test new model
        new_results = new_model(img_path, conf=0.25, iou=0.7)
        new_result = new_results[0]
        new_detections = len(new_result.boxes)
        new_false_positives += new_detections
        
        # Compare
        reduction = old_detections - new_detections
        if reduction > 0:
            images_with_improvement += 1
        
        print(f"   Old model: {old_detections} false positives")
        print(f"   New model: {new_detections} false positives")
        
        if reduction > 0:
            print(f"   ✓ Reduced by {reduction} false positives")
        elif reduction < 0:
            print(f"   ⚠ Increased by {abs(reduction)} false positives")
        else:
            print(f"   = Same number of false positives")
        
        # Show confidence scores if detections exist
        if old_detections > 0:
            old_conf = [box.conf.item() for box in old_result.boxes]
            print(f"   Old confidences: {[f'{c:.3f}' for c in old_conf]}")
        if new_detections > 0:
            new_conf = [box.conf.item() for box in new_result.boxes]
            print(f"   New confidences: {[f'{c:.3f}' for c in new_conf]}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY - NEGATIVE EXAMPLES TEST")
    print("="*70)
    print(f"Total negative images tested: {len(negative_images)}")
    print(f"Images with reduced false positives: {images_with_improvement}")
    print(f"Old model false positives: {old_false_positives}")
    print(f"New model false positives: {new_false_positives}")
    print(f"Overall reduction: {old_false_positives - new_false_positives} false positives")
    
    if old_false_positives > 0:
        reduction_percent = ((old_false_positives - new_false_positives) / old_false_positives) * 100
        print(f"Reduction percentage: {reduction_percent:.1f}%")
    
    # Success criteria
    print("\n" + "-"*70)
    print("EVALUATION:")
    if new_false_positives < old_false_positives:
        print("✓ SUCCESS: New model has fewer false positives!")
        if reduction_percent > 50:
            print("✓ Excellent improvement (>50% reduction)")
        elif reduction_percent > 25:
            print("✓ Good improvement (>25% reduction)")
        else:
            print("~ Moderate improvement")
    elif new_false_positives == old_false_positives:
        print("~ No change in false positives")
    else:
        print("⚠ Regression: New model has more false positives")
    
    print("="*70)
    
    # Save visualizations for comparison
    output_dir = Path('model/detection/negative_test_results')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\nSaving comparison visualizations...")
    for i, img_path in enumerate(negative_images[:10]):  # First 10 images
        old_results = old_model(img_path, conf=0.25, iou=0.7)
        new_results = new_model(img_path, conf=0.25, iou=0.7)
        
        old_results[0].save(filename=output_dir / f"old_{img_path.name}")
        new_results[0].save(filename=output_dir / f"new_{img_path.name}")
        
        print(f"Saved: old_{img_path.name} and new_{img_path.name}")

if __name__ == '__main__':
    test_negative_examples()