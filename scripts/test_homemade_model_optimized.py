#!/usr/bin/env python3
"""
Test the trained homemade model with optimized parameters for multiple detections
"""

from ultralytics import YOLO
from pathlib import Path

def test_homemade_model_optimized():
    """Test the trained model with optimized parameters"""
    
    model_path = 'model/detection/homemade_yolov8n_100epochs_expanded/weights/best.pt'
    test_images_dir = 'model/dataset_homemade_labeled/test/images'
    output_dir = 'model/detection/homemade_yolov8n_100epochs_expanded/test_results_optimized'
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("TESTING HOMEMADE MODEL - OPTIMIZED PARAMETERS")
    print("="*60)
    print(f"Model: {model_path}")
    print(f"Test images: {test_images_dir}")
    print(f"Output: {output_dir}")
    print("Parameters: conf=0.15, iou=0.85 (optimized for multiple detections)")
    print("="*60)
    
    # Load model
    model = YOLO(model_path)
    
    # Get test images
    test_images = list(Path(test_images_dir).glob('*.jpg'))
    
    if not test_images:
        print("No test images found!")
        return
    
    print(f"Found {len(test_images)} test images")
    
    # Statistics
    total_detections = 0
    images_with_detections = 0
    images_with_multiple_detections = 0
    
    # Run inference on each test image
    for i, img_path in enumerate(test_images):
        print(f"\nTesting image {i+1}: {img_path.name}")
        
        # Run inference with optimized parameters
        results = model(img_path, conf=0.15, iou=0.85)
        
        # Get result
        result = results[0]
        
        # Count detections
        num_detections = len(result.boxes)
        total_detections += num_detections
        
        if num_detections > 0:
            images_with_detections += 1
            if num_detections > 1:
                images_with_multiple_detections += 1
        
        # Print detections
        if num_detections > 0:
            print(f"  ✓ Detected {num_detections} strawberries:")
            conf_scores = []
            for j, box in enumerate(result.boxes):
                conf = box.conf.item()
                conf_scores.append(conf)
                print(f"    - Detection {j+1}: {conf:.3f} confidence")
            print(f"    Confidence range: {min(conf_scores):.3f} - {max(conf_scores):.3f}")
        else:
            print("  ✗ No strawberries detected")
        
        # Save visualization
        output_path = f"{output_dir}/test_result_{img_path.name}"
        result.save(filename=output_path)
        print(f"  Saved visualization: {output_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Images tested: {len(test_images)}")
    print(f"Images with detections: {images_with_detections}")
    print(f"Images with multiple detections: {images_with_multiple_detections}")
    print(f"Total detections: {total_detections}")
    print(f"Average detections per image: {total_detections/len(test_images):.2f}")
    print("="*60)

if __name__ == '__main__':
    test_homemade_model_optimized()