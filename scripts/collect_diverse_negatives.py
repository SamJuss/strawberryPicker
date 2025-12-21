#!/usr/bin/env python3
"""
Collect diverse negative examples to reduce false positives.
This script helps gather images of common false positive objects.
"""

import os
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime

def create_synthetic_negatives(category, count=20, output_dir="model/dataset_homemade/negative_examples"):
    """
    Create synthetic negative examples for categories where real images aren't available.
    """
    output_path = Path(output_dir) / category
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Creating {count} synthetic {category} examples...")

    for i in range(count):
        # Create a random colored image
        height, width = np.random.randint(300, 800), np.random.randint(300, 800)
        image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)

        # Add some random patterns based on category
        if 'red' in category.lower():
            # Make it reddish
            image[:, :, 2] = np.random.randint(150, 255, (height, width))  # Red channel
            image[:, :, 0] = np.random.randint(0, 100, (height, width))    # Blue channel
            image[:, :, 1] = np.random.randint(0, 100, (height, width))    # Green channel
        elif 'fruit' in category.lower():
            # Add circular shapes
            for _ in range(np.random.randint(1, 5)):
                center = (np.random.randint(50, width-50), np.random.randint(50, height-50))
                radius = np.random.randint(20, 80)
                color = tuple(np.random.randint(0, 255, 3).tolist())
                cv2.circle(image, center, radius, color, -1)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"synthetic_neg_{category}_{timestamp}_{i:03d}.jpg"
        filepath = output_path / filename

        cv2.imwrite(str(filepath), image)

        # Create empty label file
        label_file = filepath.with_suffix('.txt')
        label_file.touch()

        print(f"  Created: {filename}")

    return count

def main():
    print("=== Diverse Negative Example Collection ===")
    print("Creating synthetic negative examples to reduce false positives")
    print("")

    # Create synthetic examples for different categories
    categories = [
        ('red_objects', 15),
        ('other_fruits', 15),
        ('random_objects', 25)
    ]

    total_collected = 0

    for category, count in categories:
        print(f"\n{'='*50}")
        print(f"Creating {count} synthetic {category} examples")
        print('='*50)

        collected = create_synthetic_negatives(category, count)
        total_collected += collected
        print(f"Created {collected} images for {category}")

    print(f"\n{'='*50}")
    print(f"COLLECTION COMPLETE: {total_collected} synthetic negative examples")
    print('='*50)
    print("\nNext steps:")
    print("1. Review the images in model/dataset_homemade/negative_examples/")
    print("2. Add real webcam images for fingers_hands and backgrounds categories")
    print("3. Run: python3 scripts/fix_dataset_with_negatives.py")
    print("4. Run: python3 scripts/prepare_homemade_dataset.py")
    print("5. Retrain: python3 scripts/train_improved_model.py")
    print("6. Test: python3 scripts/test_negative_examples.py")

if __name__ == '__main__':
    main()