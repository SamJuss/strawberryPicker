#!/usr/bin/env python3
"""
Collect real-world negative examples that are causing false positives.
"""

import cv2
import numpy as np
from pathlib import Path
from datetime import datetime

def collect_negative_examples(category, target_count=10, output_dir="model/dataset_homemade/negative_examples"):
    """
    Collect negative examples from webcam for specific categories.
    """
    output_path = Path(output_dir) / category
    output_path.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print(f"Error: Cannot open webcam for {category}")
        return 0

    print(f"\n=== Collecting {target_count} {category} images ===")
    print("Position the object in front of the camera")
    print("Press SPACE to capture, 'q' to quit")

    count = 0
    while count < target_count:
        ret, frame = cap.read()
        if not ret:
            break

        # Show the frame
        cv2.putText(frame, f"{category}: {count}/{target_count}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, "SPACE: capture, Q: quit", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow('Negative Example Collection', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # Spacebar
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"real_world_neg_{category}_{timestamp}_{count:03d}.jpg"
            filepath = output_path / filename

            cv2.imwrite(str(filepath), frame)
            print(f"  Saved: {filename}")

            # Create empty label file
            label_file = filepath.with_suffix('.txt')
            label_file.touch()

            count += 1

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return count

def main():
    print("=== Real-World Negative Example Collection ===")
    print("Collect images of objects that are causing false positives")
    print()

    # Categories based on user's feedback
    categories = {
        'necks_skin': {'count': 15, 'description': 'Necks, arms, skin, human body parts'},
        'shelves_surfaces': {'count': 15, 'description': 'Empty shelves, tables, surfaces'},
        'clothing_fabric': {'count': 10, 'description': 'Clothing, fabric, textiles'},
        'faces': {'count': 10, 'description': 'Human faces from different angles'},
        'backgrounds': {'count': 10, 'description': 'Empty backgrounds, walls, floors'}
    }

    total_collected = 0

    for category, config in categories.items():
        print(f"\n{'='*60}")
        print(f"Category: {category}")
        print(f"Description: {config['description']}")
        print(f"Target: {config['count']} images")
        print('='*60)

        collected = collect_negative_examples(category, config['count'])
        total_collected += collected
        print(f"Collected {collected} images for {category}")

    print(f"\n{'='*60}")
    print(f"COLLECTION COMPLETE: {total_collected} real-world negative examples")
    print('='*60)
    print("\nNext steps:")
    print("1. Review collected images")
    print("2. Run: python3 scripts/fix_dataset_with_negatives.py")
    print("3. Run: python3 scripts/prepare_homemade_dataset.py")
    print("4. Retrain: python3 scripts/train_improved_model.py")
    print("5. Test: python3 scripts/test_negative_examples.py")

if __name__ == '__main__':
    main()