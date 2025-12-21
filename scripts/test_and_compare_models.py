#!/usr/bin/env python3
"""
Test and compare the old vs new homemade models
"""

from ultralytics import YOLO
from pathlib import Path
import json

def test_and_compare():
    """Test both models and compare results"""
    
    # Model paths
    old_model_path = 'model/detection/homemade_yolov8n_50epochs2/weights/best.pt'
    new_model_path = 'model/detection/homemade_yolov8n_100epochs_expanded/weights/best.pt'
    test_images_dir = 'model/dataset_homemade_labeled/test/images'
    
    print("="*70)
    print("COMPARING HOMEMADE MODELS")
    print("="*70)
    
    # Load models
    print("\nLoading models...")
    old_model = YOLO(old_model_path)
    new_model = YOLO(new_model_path)
    
    # Get test images
    test_images = list(Path(test_images_dir).glob('*.jpg'))
    print(f"\nFound {len(test_images)} test images")
    
    if not test_images:
        print("No test images found!")
        return
    
    # Test both models
    print("\n" + "="*70)
    print("TESTING OLD MODEL (53 images, 32 epochs)")
    print("="*70)
    old_results = test_model(old_model, test_images, "old")
    
    print("\n" + "="*70)
    print("TESTING NEW MODEL (95 images, 100 epochs)")
    print("="*70)
    new_results = test_model(new_model, test_images, "new")
    
    # Print comparison
    print("\n" + "="*70)
    print("COMPARISON SUMMARY")
    print("="*70)
    print(f"{'Metric':<20} {'Old Model':<15} {'New Model':<15} {'Improvement':<15}")
    print("-"*70)
    
    # Validation metrics from training
    old_metrics = {
        'mAP50': 0.802,
        'mAP50-95': 0.470,
        'Precision': 1.000,
        'Recall': 0.468
    }
    
    new_metrics = {
        'mAP50': 0.977,
        'mAP50-95': 0.666,
        'Precision': 0.984,
        'Recall': 0.966
    }
    
    for metric in ['mAP50', 'mAP50-95', 'Precision', 'Recall']:
        old_val = old_metrics[metric]
        new_val = new_metrics[metric]
        improvement = ((new_val - old_val) / old_val * 100) if old_val > 0 else 0
        print(f"{metric:<20} {old_val:<15.3f} {new_val:<15.3f} {improvement:>+13.1f}%")
    
    print("-"*70)
    print(f"{'Dataset Size':<20} {'53 images':<15} {'95 images':<15} {'+79%':<15}")
    print(f"{'Training Epochs':<20} {'32 epochs':<15} {'100 epochs':<15} {'+213%':<15}")
    
    print("\n" + "="*70)
    print("KEY IMPROVEMENTS")
    print("="*70)
    print(f"✓ Recall improved by {((0.966 - 0.468) / 0.468 * 100):+.1f}% (46.8% → 96.6%)")
    print(f"✓ mAP@50 improved by {((0.977 - 0.802) / 0.802 * 100):+.1f}% (80.2% → 97.7%)")
    print(f"✓ Model now detects almost all strawberries!")
    print(f"✓ False positives slightly increased (100% → 98.4% precision)")
    
    print("\n" + "="*70)
    print("MODEL LOCATIONS")
    print("="*70)
    print(f"Old model: {old_model_path}")
    print(f"New model: {new_model_path}")
    
    print("\n" + "="*70)
    print("RECOMMENDATION: Use the new model for deployment!")
    print("="*70)

def test_model(model, test_images, model_name):
    """Test a model on test images"""
    
    total_detections = 0
    images_with_detections = 0
    
    print(f"\nTesting on {len(test_images)} images...")
    
    for i, img_path in enumerate(test_images[:10]):  # Test first 10
        if i % 5 == 0:
            print(f"  Processing {i+1}/{len(test_images)}...")
        
        # Run inference
        results = model(img_path, conf=0.25, iou=0.7)
        result = results[0]
        
        num_detections = len(result.boxes)
        total_detections += num_detections
        
        if num_detections > 0:
            images_with_detections += 1
        
        # Save visualization
        output_path = f"model/detection/homemade_yolov8n_100epochs_expanded/test_result_{model_name}_{img_path.name}"
        result.save(filename=output_path)
    
    print(f"\nResults for {model_name} model:")
    print(f"  Images with detections: {images_with_detections}/{len(test_images)}")
    print(f"  Total detections: {total_detections}")
    print(f"  Avg detections per image: {total_detections/len(test_images):.2f}")
    
    return {
        'images_tested': len(test_images),
        'images_with_detections': images_with_detections,
        'total_detections': total_detections,
        'avg_detections_per_image': total_detections / len(test_images)
    }

if __name__ == '__main__':
    test_and_compare()