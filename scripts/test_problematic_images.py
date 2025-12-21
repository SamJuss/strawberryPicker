#!/usr/bin/env python3
"""
Test the improved model on problematic images (body parts, red objects)
"""

from ultralytics import YOLO
from pathlib import Path
import sys

def test_problematic_images():
    """Test both old and new models on problematic images"""
    
    # Model paths
    old_model_path = 'model/detection/homemade_yolov8n_100epochs_expanded/weights/best.pt'
    new_model_path = 'model/detection/homemade_yolov8n_v2_negatives/weights/best.pt'
    
    # Load models
    print("="*70)
    print("TESTING MODELS ON PROBLEMATIC IMAGES")
    print("="*70)
    print(f"Old model: {old_model_path}")
    print(f"New model: {new_model_path}")
    print("="*70)
    
    old_model = YOLO(old_model_path)
    new_model = YOLO(new_model_path)
    
    # Test images directory (should contain body parts, red objects, etc.)
    test_dir = 'model/dataset_homemade_labeled/test/images'
    test_images = list(Path(test_dir).glob('*.jpg'))
    
    if not test_images:
        print("No test images found!")
        return
    
    print(f"\nFound {len(test_images)} test images")
    print("Testing with conf=0.25, iou=0.7")
    print("-"*70)
    
    # Statistics
    old_total_detections = 0
    new_total_detections = 0
    images_with_reduction = 0
    
    for i, img_path in enumerate(test_images):
        print(f"\n{i+1}. Testing: {img_path.name}")
        
        # Test old model
        old_results = old_model(img_path, conf=0.25, iou=0.7)
        old_result = old_results[0]
        old_detections = len(old_result.boxes)
        old_total_detections += old_detections
        
        # Test new model
        new_results = new_model(img_path, conf=0.25, iou=0.7)
        new_result = new_results[0]
        new_detections = len(new_result.boxes)
        new_total_detections += new_detections
        
        # Compare
        reduction = old_detections - new_detections
        if reduction > 0:
            images_with_reduction += 1
        
        print(f"   Old model: {old_detections} detections")
        print(f"   New model: {new_detections} detections")
        
        if reduction > 0:
            print(f"   ✓ Reduced by {reduction} detections")
        elif reduction < 0:
            print(f"   ⚠ Increased by {abs(reduction)} detections")
        else:
            print(f"   = Same number of detections")
        
        # Show confidence scores if detections differ
        if old_detections != new_detections:
            if old_detections > 0:
                old_conf = [box.conf.item() for box in old_result.boxes]
                print(f"   Old confidences: {[f'{c:.3f}' for c in old_conf]}")
            if new_detections > 0:
                new_conf = [box.conf.item() for box in new_result.boxes]
                print(f"   New confidences: {[f'{c:.3f}' for c in new_conf]}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total images tested: {len(test_images)}")
    print(f"Images with reduced detections: {images_with_reduction}")
    print(f"Old model total detections: {old_total_detections}")
    print(f"New model total detections: {new_total_detections}")
    print(f"Overall reduction: {old_total_detections - new_total_detections} detections")
    
    if old_total_detections > 0:
        reduction_percent = ((old_total_detections - new_total_detections) / old_total_detections) * 100
        print(f"Reduction percentage: {reduction_percent:.1f}%")
    
    print("="*70)
    
    # Save visualizations for comparison
    output_dir = Path('model/detection/comparison_results')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Test a few images and save comparisons
    print("\nSaving comparison visualizations...")
    for i, img_path in enumerate(test_images[:5]):  # First 5 images
        old_results = old_model(img_path, conf=0.25, iou=0.7)
        new_results = new_model(img_path, conf=0.25, iou=0.7)
        
        old_results[0].save(filename=output_dir / f"old_{img_path.name}")
        new_results[0].save(filename=output_dir / f"new_{img_path.name}")
        
        print(f"Saved: old_{img_path.name} and new_{img_path.name}")

if __name__ == '__main__':
    test_problematic_images()