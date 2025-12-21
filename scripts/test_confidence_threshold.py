#!/usr/bin/env python3
"""
Test different confidence thresholds to reduce false positives.
"""

import os
from pathlib import Path
from ultralytics import YOLO

def test_confidence_thresholds(model_path, test_images, thresholds=[0.1, 0.25, 0.5, 0.75, 0.9]):
    """
    Test model with different confidence thresholds.
    """
    model = YOLO(model_path)

    print("=== CONFIDENCE THRESHOLD TESTING ===")
    print(f"Model: {model_path}")
    print(f"Test images: {len(test_images)}")
    print()

    results_summary = {}

    for conf in thresholds:
        print(f"Testing confidence threshold: {conf}")
        print("-" * 50)

        total_detections = 0
        total_images = len(test_images)

        for img_path in test_images:
            results = model(img_path, conf=conf, verbose=False)

            detections = len(results[0].boxes) if results[0].boxes is not None else 0
            total_detections += detections

            if detections > 0:
                print(f"  {Path(img_path).name}: {detections} detections")
                if results[0].boxes is not None:
                    confidences = results[0].boxes.conf.cpu().numpy()
                    print(f"    Confidences: {confidences}")

        avg_detections = total_detections / total_images
        results_summary[conf] = {
            'total_detections': total_detections,
            'avg_detections_per_image': avg_detections
        }

        print(".2f")
        print()

    print("=== SUMMARY ===")
    print("Confidence | Total Detections | Avg per Image")
    print("------------|------------------|--------------")
    for conf in sorted(results_summary.keys()):
        data = results_summary[conf]
        print("6.2f")

    return results_summary

def main():
    # Use the latest model
    model_path = "model/detection/homemade_yolov8n_v2_negatives4/weights/best.pt"

    # Test on some negative examples
    negative_dir = Path("model/dataset_homemade")
    test_images = []

    # Get some negative examples
    for img_file in negative_dir.glob("WIN_*_Pro.jpg"):
        if img_file.with_suffix('.txt').exists():
            with open(img_file.with_suffix('.txt'), 'r') as f:
                if not f.read().strip():  # Empty label = negative
                    test_images.append(str(img_file))
                    if len(test_images) >= 5:  # Test on 5 images
                        break

    if not test_images:
        print("No negative examples found for testing")
        return

    print(f"Found {len(test_images)} negative examples for testing")

    # Test different confidence thresholds
    results = test_confidence_thresholds(model_path, test_images)

    print("\n=== RECOMMENDATIONS ===")
    print("Based on the results above, choose a confidence threshold that:")
    print("- Minimizes false positives on negative examples")
    print("- Still maintains good detection on actual strawberries")
    print()
    print("For deployment, you might want to use conf=0.5 or higher")
    print("to significantly reduce false positives.")

if __name__ == '__main__':
    main()