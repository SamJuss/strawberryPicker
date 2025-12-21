#!/usr/bin/env python3
"""
Test strawberry detection with higher confidence threshold.
"""

from pathlib import Path
from ultralytics import YOLO

def test_strawberry_detection(model_path, strawberry_images, conf_threshold=0.5):
    """
    Test detection on actual strawberry images with specified confidence.
    """
    model = YOLO(model_path)

    print(f"=== TESTING STRAWBERRY DETECTION (conf={conf_threshold}) ===")
    print(f"Model: {Path(model_path).name}")
    print(f"Test images: {len(strawberry_images)}")
    print()

    total_detections = 0
    images_with_detections = 0

    for img_path in strawberry_images:
        results = model(img_path, conf=conf_threshold, verbose=False)

        detections = len(results[0].boxes) if results[0].boxes is not None else 0
        total_detections += detections

        if detections > 0:
            images_with_detections += 1
            print(f"✓ {Path(img_path).name}: {detections} detections")
            if results[0].boxes is not None:
                confidences = results[0].boxes.conf.cpu().numpy()
                print(f"  Confidences: {['.3f' for c in confidences]}")
        else:
            print(f"✗ {Path(img_path).name}: No detections")

    print()
    print("=== RESULTS ===")
    print(f"Images with detections: {images_with_detections}/{len(strawberry_images)} ({images_with_detections/len(strawberry_images)*100:.1f}%)")
    print(f"Total detections: {total_detections}")
    print(".2f")

    return {
        'images_with_detections': images_with_detections,
        'total_images': len(strawberry_images),
        'total_detections': total_detections,
        'avg_detections': total_detections / len(strawberry_images)
    }

def main():
    model_path = "model/detection/homemade_yolov8n_v2_negatives4/weights/best.pt"

    # Get some strawberry images from the dataset
    dataset_dir = Path("model/dataset_homemade_labeled/train/images")
    strawberry_images = list(dataset_dir.glob("*.jpg"))[:10]  # Test on 10 images

    if not strawberry_images:
        print("No strawberry images found for testing")
        return

    print(f"Testing on {len(strawberry_images)} strawberry images")
    print()

    # Test with different confidence thresholds
    thresholds = [0.25, 0.5, 0.75]

    results = {}
    for conf in thresholds:
        print(f"Testing with confidence threshold: {conf}")
        print("=" * 50)
        result = test_strawberry_detection(model_path, strawberry_images, conf)
        results[conf] = result
        print()

    print("=== COMPARISON SUMMARY ===")
    print("Confidence | Images Detected | Total Detections | Avg per Image")
    print("------------|----------------|------------------|---------------")
    for conf in sorted(results.keys()):
        r = results[conf]
        print("6.2f")

    print()
    print("=== RECOMMENDATIONS ===")
    print("Choose the highest confidence threshold that still detects")
    print("most strawberry images. For example:")
    print("- conf=0.5: Good balance of precision and recall")
    print("- conf=0.75: Higher precision, lower recall")

if __name__ == '__main__':
    main()