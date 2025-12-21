#!/usr/bin/env python3
"""
Debug script for multiple strawberry detection
"""

from ultralytics import YOLO
from pathlib import Path
import sys

def debug_detections(image_path, model_path):
    """Debug detection issues"""
    
    model = YOLO(model_path)
    
    print("="*60)
    print("DEBUGGING MULTIPLE DETECTIONS")
    print("="*60)
    
    # Test different confidence thresholds
    print(f"\nTesting image: {image_path}")
    print("-" * 40)
    
    for conf in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]:
        results = model(image_path, conf=conf, iou=0.7)
        num_detections = len(results[0].boxes)
        print(f"conf={conf:<4} → {num_detections} detections")
    
    # Test different IoU thresholds
    print("\n" + "-" * 40)
    print("Testing IoU thresholds (with conf=0.15):")
    
    for iou in [0.5, 0.6, 0.7, 0.8, 0.85, 0.9]:
        results = model(image_path, conf=0.15, iou=iou)
        num_detections = len(results[0].boxes)
        print(f"iou={iou:<4} → {num_detections} detections")
    
    # Show best combination
    print("\n" + "-" * 40)
    results = model(image_path, conf=0.15, iou=0.85)
    result = results[0]
    
    print(f"Best settings (conf=0.15, iou=0.85):")
    print(f"Detections: {len(result.boxes)}")
    
    for i, box in enumerate(result.boxes):
        conf = box.conf.item()
        print(f"  Detection {i+1}: {conf:.3f} confidence")
    
    # Save visualization
    output_path = 'debug_detection_result.jpg'
    result.save(filename=output_path)
    print(f"\nSaved visualization: {output_path}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Use a test image
        test_images = list(Path('model/dataset_homemade_labeled/test/images').glob('*.jpg'))
        if test_images:
            image_path = str(test_images[0])
        else:
            print("No test images found!")
            sys.exit(1)
    
    model_path = 'model/detection/homemade_yolov8n_100epochs_expanded/weights/best.pt'
    debug_detections(image_path, model_path)