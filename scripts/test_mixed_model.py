#!/usr/bin/env python3
"""
Test the mixed dataset model on homemade test images
"""

import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import argparse

def test_mixed_model(model_path, test_dir, output_dir=None, conf_threshold=0.5):
    """Test mixed model on homemade test images"""
    
    # Setup paths
    model_path = Path(model_path)
    test_dir = Path(test_dir)
    
    if output_dir is None:
        output_dir = model_path.parent.parent / "test_results_mixed"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    print(f"🧪 Testing Mixed Model: {model_path.name}")
    print(f"📁 Test directory: {test_dir}")
    print(f"📊 Confidence threshold: {conf_threshold}")
    print("=" * 60)
    
    # Load model
    model = YOLO(str(model_path))
    
    # Find test images
    test_images = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))
    
    if not test_images:
        print(f"❌ No test images found in {test_dir}")
        return
    
    print(f"Found {len(test_images)} test images")
    
    results_summary = {
        'total_images': len(test_images),
        'images_with_detections': 0,
        'total_detections': 0,
        'avg_confidence': 0.0,
        'detections_by_confidence': {'high': 0, 'medium': 0, 'low': 0}
    }
    
    all_confidences = []
    
    for i, img_path in enumerate(test_images, 1):
        print(f"\n📸 Testing image {i}: {img_path.name}")
        
        # Run inference
        results = model(img_path, conf=conf_threshold, verbose=False)
        
        detections = []
        if results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()
            
            for box, conf in zip(boxes, confidences):
                if conf >= conf_threshold:
                    detections.append({
                        'bbox': box.tolist(),
                        'confidence': float(conf)
                    })
                    all_confidences.append(float(conf))
        
        num_detections = len(detections)
        
        # Update summary
        if num_detections > 0:
            results_summary['images_with_detections'] += 1
            results_summary['total_detections'] += num_detections
            
            # Categorize by confidence
            for det in detections:
                conf = det['confidence']
                if conf >= 0.8:
                    results_summary['detections_by_confidence']['high'] += 1
                elif conf >= 0.5:
                    results_summary['detections_by_confidence']['medium'] += 1
                else:
                    results_summary['detections_by_confidence']['low'] += 1
        
        # Print results
        if num_detections == 0:
            print(f"  ✗ No strawberries detected")
        else:
            print(f"  ✓ Detected {num_detections} strawberry(s):")
            for j, det in enumerate(detections, 1):
                conf_pct = det['confidence'] * 100
                print(f"    {j}. {conf_pct:.1f}% confidence")
        
        # Save visualization
        result_img = results[0].plot()
        output_path = output_dir / f"test_result_{img_path.name}"
        cv2.imwrite(str(output_path), result_img)
        print(f"  Saved visualization: {output_path.name}")
    
    # Calculate average confidence
    if all_confidences:
        results_summary['avg_confidence'] = np.mean(all_confidences)
    
    # Print final summary
    print("\n" + "=" * 60)
    print("🎯 TESTING COMPLETED!")
    print("=" * 60)
    print(f"Total images tested: {results_summary['total_images']}")
    print(f"Images with detections: {results_summary['images_with_detections']}")
    print(f"Total detections: {results_summary['total_detections']}")
    print(f"Detection rate: {results_summary['images_with_detections']/results_summary['total_images']*100:.1f}%")
    
    if all_confidences:
        print(f"Average confidence: {results_summary['avg_confidence']*100:.1f}%")
        print(f"High confidence (≥80%): {results_summary['detections_by_confidence']['high']}")
        print(f"Medium confidence (50-79%): {results_summary['detections_by_confidence']['medium']}")
        print(f"Low confidence (<50%): {results_summary['detections_by_confidence']['low']}")
    
    print(f"\n📁 Results saved to: {output_dir}")
    
    return results_summary

def main():
    parser = argparse.ArgumentParser(description='Test mixed dataset model')
    parser.add_argument('--model', type=str, 
                       default='model/detection/mixed_conservative_v24/weights/best.pt',
                       help='Path to trained model')
    parser.add_argument('--data', type=str, 
                       default='model/dataset_homemade_labeled',
                       help='Path to test dataset directory')
    parser.add_argument('--conf', type=float, default=0.5,
                       help='Confidence threshold')
    parser.add_argument('--output', type=str, default=None,
                       help='Output directory for results')
    
    args = parser.parse_args()
    
    test_dir = Path(args.data) / 'test' / 'images'
    
    test_mixed_model(
        model_path=args.model,
        test_dir=test_dir,
        output_dir=args.output,
        conf_threshold=args.conf
    )

if __name__ == '__main__':
    main()