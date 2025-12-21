#!/usr/bin/env python3
"""
Test the trained homemade model on sample images
"""

from ultralytics import YOLO
from pathlib import Path
import cv2
import numpy as np

def test_homemade_model():
    """Test the trained model on sample images"""
    
    model_path = 'model/detection/homemade_yolov8n_50epochs2/weights/best.pt'
    test_images_dir = 'model/dataset_homemade_labeled/test/images'
    
    print("="*60)
    print("TESTING HOMEMADE MODEL")
    print("="*60)
    print(f"Model: {model_path}")
    print(f"Test images: {test_images_dir}")
    print("="*60)
    
    # Load model
    model = YOLO(model_path)
    
    # Get test images
    test_images = list(Path(test_images_dir).glob('*.jpg'))
    
    if not test_images:
        print("No test images found!")
        return
    
    print(f"Found {len(test_images)} test images")
    
    # Run inference on each test image
    for i, img_path in enumerate(test_images[:5]):  # Test first 5 images
        print(f"\nTesting image {i+1}: {img_path.name}")
        
        # Run inference
        results = model(img_path, conf=0.25, iou=0.7)
        
        # Get result
        result = results[0]
        
        # Print detections
        if len(result.boxes) > 0:
            print(f"  ✓ Detected {len(result.boxes)} strawberries:")
            for j, box in enumerate(result.boxes):
                conf = box.conf.item()
                print(f"    - Detection {j+1}: {conf:.2f} confidence")
        else:
            print("  ✗ No strawberries detected")
        
        # Save visualization
        output_path = f"model/detection/homemade_yolov8n_50epochs2/test_result_{img_path.name}"
        result.save(filename=output_path)
        print(f"  Saved visualization: {output_path}")
    
    print("\n" + "="*60)
    print("TESTING COMPLETED!")
    print("="*60)

if __name__ == '__main__':
    test_homemade_model()