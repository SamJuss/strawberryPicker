#!/usr/bin/env python3
"""
Production-ready strawberry detector with optimized confidence threshold.
"""

import cv2
import time
from pathlib import Path
from ultralytics import YOLO

class StrawberryDetector:
    def __init__(self, model_path="model/detection/homemade_yolov8n_v2_negatives4/weights/best.pt", conf_threshold=0.5):
        """
        Initialize the strawberry detector.

        Args:
            model_path: Path to the YOLO model
            conf_threshold: Confidence threshold (0.5 recommended for production)
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        print(f"Loaded model: {model_path}")
        print(f"Confidence threshold: {conf_threshold}")

    def detect_strawberries(self, image_path_or_frame):
        """
        Detect strawberries in an image.

        Args:
            image_path_or_frame: Path to image file or numpy array (frame)

        Returns:
            dict: Detection results with boxes, confidences, and count
        """
        # Run inference
        results = self.model(image_path_or_frame, conf=self.conf_threshold, verbose=False)

        # Extract detections
        detections = []
        if results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
            confidences = results[0].boxes.conf.cpu().numpy()
            class_ids = results[0].boxes.cls.cpu().numpy().astype(int)

            for box, conf, class_id in zip(boxes, confidences, class_ids):
                detections.append({
                    'bbox': box.tolist(),
                    'confidence': float(conf),
                    'class_id': int(class_id),
                    'class_name': 'strawberry'
                })

        return {
            'detections': detections,
            'count': len(detections),
            'image_shape': results[0].orig_shape
        }

    def draw_detections(self, image, detections):
        """
        Draw detection boxes on image.

        Args:
            image: OpenCV image
            detections: Detection results from detect_strawberries()

        Returns:
            image: Image with drawn detections
        """
        for det in detections['detections']:
            x1, y1, x2, y2 = map(int, det['bbox'])
            conf = det['confidence']

            # Draw rectangle
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw label
            label = f"Strawberry: {conf:.2f}"
            cv2.putText(image, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, (0, 255, 0), 2)

        # Draw count
        count_text = f"Detected: {detections['count']} strawberries"
        cv2.putText(image, count_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                   1, (255, 255, 255), 2)

        return image

def test_on_sample_images():
    """Test the detector on sample images."""
    detector = StrawberryDetector()

    # Test on some images
    test_dir = Path("model/dataset_homemade_labeled/test/images")
    if test_dir.exists():
        test_images = list(test_dir.glob("*.jpg"))[:5]

        print(f"\n=== TESTING ON {len(test_images)} SAMPLE IMAGES ===")

        for img_path in test_images:
            print(f"\nTesting: {img_path.name}")

            # Detect strawberries
            results = detector.detect_strawberries(str(img_path))
            print(f"  Detections: {results['count']}")

            if results['count'] > 0:
                for i, det in enumerate(results['detections']):
                    print(f"    {i+1}. Confidence: {det['confidence']:.3f}")

def main():
    print("=== Strawberry Detector - Production Ready ===")
    print("Confidence threshold: 0.5 (optimized for minimal false positives)")
    print()

    # Test on sample images
    test_on_sample_images()

    print("\n=== USAGE EXAMPLES ===")
    print("""
# Initialize detector
detector = StrawberryDetector()

# Detect in image file
results = detector.detect_strawberries("path/to/image.jpg")
print(f"Found {results['count']} strawberries")

# Detect in webcam frame (numpy array)
# results = detector.detect_strawberries(frame)

# Draw detections on image
annotated_image = detector.draw_detections(image, results)
cv2.imshow("Detections", annotated_image)
    """)

if __name__ == '__main__':
    main()