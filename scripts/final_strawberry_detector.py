#!/usr/bin/env python3
"""
FINAL PRODUCTION STRAWBERRY DETECTOR - Optimized for Real-World Use
"""

import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

class ProductionStrawberryDetector:
    def __init__(self, model_path="model/detection/homemade_yolov8n_v2_negatives5/weights/best.pt", conf_threshold=0.7):
        """
        Production-ready strawberry detector with conservative settings.

        Args:
            model_path: Path to the trained model
            conf_threshold: High confidence threshold (0.7) to minimize false positives
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        print(f"🎯 Production Strawberry Detector Loaded")
        print(f"   Model: {Path(model_path).name}")
        print(f"   Confidence threshold: {conf_threshold} (conservative)")
        print(f"   Purpose: Minimize false positives on necks, shelves, clothing")

    def detect_strawberries(self, image):
        """
        Detect strawberries with high confidence.

        Args:
            image: OpenCV image or path to image file

        Returns:
            dict: Detection results
        """
        # Run inference with conservative settings
        results = self.model(image, conf=self.conf_threshold, iou=0.7, verbose=False)

        detections = []
        if results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()

            for box, conf in zip(boxes, confidences):
                if conf >= self.conf_threshold:  # Double-check threshold
                    detections.append({
                        'bbox': box.tolist(),
                        'confidence': float(conf),
                        'class': 'strawberry'
                    })

        return {
            'detections': detections,
            'count': len(detections),
            'conf_threshold': self.conf_threshold
        }

    def is_strawberry_present(self, image):
        """
        Quick check if any strawberries are detected.

        Args:
            image: Input image

        Returns:
            bool: True if strawberries detected with high confidence
        """
        results = self.detect_strawberries(image)
        return results['count'] > 0

    def get_detection_summary(self, image):
        """
        Get a human-readable summary of detections.

        Args:
            image: Input image

        Returns:
            str: Summary text
        """
        results = self.detect_strawberries(image)

        if results['count'] == 0:
            return "❌ No strawberries detected (clean scene)"

        summary = f"✅ Found {results['count']} strawberry(s):\n"
        for i, det in enumerate(results['detections'], 1):
            conf_pct = det['confidence'] * 100
            summary += f"   {i}. {conf_pct:.1f}% confidence\n"

        return summary

def test_production_detector():
    """Test the production detector on sample images."""
    detector = ProductionStrawberryDetector()

    # Test on some images
    test_dir = Path("model/dataset_homemade_labeled/test/images")
    if test_dir.exists():
        test_images = list(test_dir.glob("*.jpg"))[:5]

        print(f"\n🧪 TESTING PRODUCTION DETECTOR (conf={detector.conf_threshold})")
        print("=" * 60)

        for img_path in test_images:
            print(f"\n📸 Testing: {img_path.name}")
            results = detector.detect_strawberries(str(img_path))
            summary = detector.get_detection_summary(str(img_path))
            print(summary)

def main():
    print("🍓 FINAL PRODUCTION STRAWBERRY DETECTOR")
    print("=" * 50)
    print("Optimized for real-world use with minimal false positives")
    print("Trained on 228 images (92 strawberries + 136 diverse negatives)")
    print("Including specific examples of necks, shelves, and clothing")
    print()

    # Test the detector
    test_production_detector()

    print("\n🚀 DEPLOYMENT INSTRUCTIONS:")
    print("=" * 50)
    print("""
# In your robot control code:

from scripts.final_strawberry_detector import ProductionStrawberryDetector

# Initialize detector
detector = ProductionStrawberryDetector()

# Check for strawberries before picking
if detector.is_strawberry_present(frame):
    print("Strawberry found - safe to pick!")
    # Proceed with picking logic
else:
    print("No strawberries detected - move to next location")
    # Move robot arm to new position

# Get detailed detection info
results = detector.detect_strawberries(frame)
for det in results['detections']:
    x1, y1, x2, y2 = det['bbox']
    confidence = det['confidence']
    # Use bounding box for precise picking
    """)

if __name__ == '__main__':
    main()