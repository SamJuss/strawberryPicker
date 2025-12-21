#!/usr/bin/env python3
"""
Generate synthetic negative examples for specific false positive categories.
"""

import cv2
import numpy as np
from pathlib import Path
from datetime import datetime

def generate_neck_skin_examples(count=20, output_dir="model/dataset_homemade/negative_examples/necks_skin"):
    """Generate synthetic neck/skin examples."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Generating {count} synthetic neck/skin examples...")

    for i in range(count):
        # Create skin-toned background
        height, width = np.random.randint(400, 800), np.random.randint(400, 800)
        image = np.zeros((height, width, 3), dtype=np.uint8)

        # Add skin-like colors and textures
        skin_colors = [
            (180, 130, 100),  # Light skin
            (150, 100, 80),   # Medium skin
            (120, 80, 60),    # Darker skin
            (200, 150, 120),  # Very light skin
        ]

        # Create skin-like patches
        for _ in range(np.random.randint(3, 8)):
            color = skin_colors[np.random.randint(len(skin_colors))]
            center_x = np.random.randint(width//4, 3*width//4)
            center_y = np.random.randint(height//4, 3*height//4)
            radius = np.random.randint(50, 150)

            # Draw irregular skin patch
            cv2.circle(image, (center_x, center_y), radius, color, -1)

            # Add some texture/noise
            noise = np.random.randint(-20, 20, (height, width, 3), dtype=np.int16)
            image = cv2.add(image.astype(np.int16), noise)
            image = np.clip(image, 0, 255).astype(np.uint8)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"synthetic_neck_skin_{timestamp}_{i:03d}.jpg"
        filepath = output_path / filename

        cv2.imwrite(str(filepath), image)

        # Create empty label file
        label_file = filepath.with_suffix('.txt')
        label_file.touch()

        print(f"  Created: {filename}")

    return count

def generate_shelf_surface_examples(count=20, output_dir="model/dataset_homemade/negative_examples/shelves_surfaces"):
    """Generate synthetic shelf/surface examples."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Generating {count} synthetic shelf/surface examples...")

    for i in range(count):
        height, width = np.random.randint(400, 800), np.random.randint(400, 800)
        image = np.zeros((height, width, 3), dtype=np.uint8)

        # Shelf-like colors (wood, metal, plastic)
        shelf_colors = [
            (150, 100, 50),   # Brown wood
            (200, 200, 200),  # Gray metal
            (100, 100, 100),  # Dark gray
            (80, 50, 30),     # Dark wood
            (220, 220, 220),  # Light gray
        ]

        # Create shelf-like horizontal surfaces
        for y in range(0, height, np.random.randint(100, 200)):
            color = shelf_colors[np.random.randint(len(shelf_colors))]
            thickness = np.random.randint(20, 60)
            cv2.rectangle(image, (0, y), (width, y + thickness), color, -1)

        # Add some texture
        noise = np.random.randint(-15, 15, (height, width, 3), dtype=np.int16)
        image = cv2.add(image.astype(np.int16), noise)
        image = np.clip(image, 0, 255).astype(np.uint8)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"synthetic_shelf_surface_{timestamp}_{i:03d}.jpg"
        filepath = output_path / filename

        cv2.imwrite(str(filepath), image)

        # Create empty label file
        label_file = filepath.with_suffix('.txt')
        label_file.touch()

        print(f"  Created: {filename}")

    return count

def generate_clothing_fabric_examples(count=15, output_dir="model/dataset_homemade/negative_examples/clothing_fabric"):
    """Generate synthetic clothing/fabric examples."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Generating {count} synthetic clothing/fabric examples...")

    for i in range(count):
        height, width = np.random.randint(400, 800), np.random.randint(400, 800)
        image = np.zeros((height, width, 3), dtype=np.uint8)

        # Clothing colors
        fabric_colors = [
            (200, 50, 50),    # Red shirt
            (50, 50, 200),    # Blue shirt
            (50, 200, 50),    # Green shirt
            (150, 150, 150),  # Gray shirt
            (200, 200, 50),   # Yellow shirt
            (150, 50, 200),   # Purple shirt
        ]

        # Create fabric-like patterns
        base_color = fabric_colors[np.random.randint(len(fabric_colors))]
        image[:, :] = base_color

        # Add fabric texture (subtle patterns)
        for _ in range(np.random.randint(5, 15)):
            x = np.random.randint(0, width)
            y = np.random.randint(0, height)
            cv2.circle(image, (x, y), np.random.randint(10, 50),
                      tuple(np.random.randint(max(0, c-30), min(255, c+30)) for c in base_color),
                      -1)

        # Add wrinkles/folds
        for _ in range(np.random.randint(3, 8)):
            start_x = np.random.randint(0, width//2)
            start_y = np.random.randint(0, height)
            end_x = np.random.randint(width//2, width)
            end_y = np.random.randint(0, height)
            cv2.line(image, (start_x, start_y), (end_x, end_y),
                    tuple(max(0, c-50) for c in base_color), np.random.randint(2, 8))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"synthetic_clothing_fabric_{timestamp}_{i:03d}.jpg"
        filepath = output_path / filename

        cv2.imwrite(str(filepath), image)

        # Create empty label file
        label_file = filepath.with_suffix('.txt')
        label_file.touch()

        print(f"  Created: {filename}")

    return count

def main():
    print("=== Generating Specific Negative Examples ===")
    print("Creating synthetic examples for false positive categories")
    print()

    total_generated = 0

    # Generate examples for each problematic category
    categories = [
        ('necks_skin', generate_neck_skin_examples, 25),
        ('shelves_surfaces', generate_shelf_surface_examples, 25),
        ('clothing_fabric', generate_clothing_fabric_examples, 20)
    ]

    for category_name, generator_func, count in categories:
        print(f"\n{'='*60}")
        print(f"Generating {count} {category_name} examples")
        print('='*60)

        generated = generator_func(count)
        total_generated += generated
        print(f"Generated {generated} images for {category_name}")

    print(f"\n{'='*60}")
    print(f"GENERATION COMPLETE: {total_generated} specific negative examples")
    print('='*60)
    print("\nNext steps:")
    print("1. Review generated images")
    print("2. Run: python3 scripts/fix_dataset_with_negatives.py")
    print("3. Run: python3 scripts/prepare_homemade_dataset.py")
    print("4. Retrain: python3 scripts/train_improved_model.py")
    print("5. Test: python3 scripts/test_negative_examples.py")

if __name__ == '__main__':
    main()