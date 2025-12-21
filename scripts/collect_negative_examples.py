#!/usr/bin/env python3
"""
Script to collect and organize negative examples for training.
Helps build a diverse set of "not strawberry" images to reduce false positives.
"""

import cv2
import numpy as np
from pathlib import Path
import argparse
import time
from datetime import datetime

class NegativeExampleCollector:
    def __init__(self, output_dir="model/dataset_homemade/negative_examples"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different types of negatives
        self.subdirs = {
            'fingers_hands': self.output_dir / 'fingers_hands',
            'red_objects': self.output_dir / 'red_objects',
            'other_fruits': self.output_dir / 'other_fruits',
            'backgrounds': self.output_dir / 'backgrounds',
            'clothing': self.output_dir / 'clothing',
            'random': self.output_dir / 'random'
        }
        
        for subdir in self.subdirs.values():
            subdir.mkdir(exist_ok=True)
        
        print(f"Negative example collector initialized")
        print(f"Output directory: {self.output_dir}")
        print("\nCategories:")
        for name, path in self.subdirs.items():
            print(f"  - {name}: {path}")
    
    def capture_from_webcam(self, category='random', num_images=20):
        """Capture negative examples from webcam"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        category_dir = self.subdirs.get(category, self.subdirs['random'])
        print(f"\nCapturing {num_images} images to {category_dir}")
        print("Press SPACE to capture, 'q' to quit early")
        
        captured = 0
        while captured < num_images:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Display instructions on frame
            display_frame = frame.copy()
            cv2.putText(display_frame, f"Capturing: {category}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_frame, f"Progress: {captured}/{num_images}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_frame, "Press SPACE to capture, 'q' to quit", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            cv2.imshow('Negative Example Capture', display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):
                # Save image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"neg_{category}_{timestamp}_{captured:03d}.jpg"
                filepath = category_dir / filename
                cv2.imwrite(str(filepath), frame)
                print(f"  Captured: {filename}")
                captured += 1
        
        cap.release()
        cv2.destroyAllWindows()
        print(f"\nCaptured {captured} images to {category_dir}")
        return captured
    
    def copy_existing_images(self, source_dir, category='random'):
        """Copy existing images from a directory as negative examples"""
        source_path = Path(source_dir)
        if not source_path.exists():
            print(f"Error: Source directory {source_path} does not exist")
            return 0
        
        category_dir = self.subdirs.get(category, self.subdirs['random'])
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        
        copied = 0
        for img_file in source_path.glob('*'):
            if img_file.suffix.lower() in image_extensions:
                # Copy and rename to avoid conflicts
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = f"neg_{category}_{timestamp}_{copied:03d}{img_file.suffix}"
                dest_path = category_dir / new_filename
                
                import shutil
                shutil.copy2(img_file, dest_path)
                copied += 1
        
        print(f"Copied {copied} images from {source_path} to {category_dir}")
        return copied
    
    def create_empty_labels(self):
        """Create empty label files for all negative examples"""
        print("\nCreating empty label files for negative examples...")
        
        total_labels = 0
        for category, category_dir in self.subdirs.items():
            for img_file in category_dir.glob('*.jpg'):
                label_file = img_file.with_suffix('.txt')
                if not label_file.exists():
                    # Create empty file (no detections)
                    label_file.touch()
                    total_labels += 1
        
        print(f"Created {total_labels} empty label files")
        return total_labels
    
    def get_stats(self):
        """Get statistics about collected negative examples"""
        stats = {}
        total_images = 0
        
        for category, category_dir in self.subdirs.items():
            count = len(list(category_dir.glob('*.jpg')))
            stats[category] = count
            total_images += count
        
        return stats, total_images

def main():
    parser = argparse.ArgumentParser(description='Collect negative examples for training')
    parser.add_argument('--mode', choices=['webcam', 'copy'], default='webcam',
                       help='Mode: webcam capture or copy existing images')
    parser.add_argument('--category', default='random',
                       choices=['fingers_hands', 'red_objects', 'other_fruits', 
                               'backgrounds', 'clothing', 'random'],
                       help='Category of negative examples')
    parser.add_argument('--num_images', type=int, default=20,
                       help='Number of images to capture (webcam mode)')
    parser.add_argument('--source_dir', type=str,
                       help='Source directory (copy mode)')
    parser.add_argument('--create_labels', action='store_true', default=True,
                       help='Create empty label files after collection')
    
    args = parser.parse_args()
    
    collector = NegativeExampleCollector()
    
    if args.mode == 'webcam':
        print(f"\n=== Webcam Capture Mode ===")
        print(f"Category: {args.category}")
        print(f"Target: {args.num_images} images")
        collector.capture_from_webcam(args.category, args.num_images)
    
    elif args.mode == 'copy':
        if not args.source_dir:
            print("Error: --source_dir required for copy mode")
            return
        print(f"\n=== Copy Mode ===")
        print(f"Source: {args.source_dir}")
        print(f"Category: {args.category}")
        collector.copy_existing_images(args.source_dir, args.category)
    
    # Create empty label files
    if args.create_labels:
        collector.create_empty_labels()
    
    # Print statistics
    stats, total = collector.get_stats()
    print(f"\n=== Collection Statistics ===")
    print(f"Total negative examples: {total}")
    for category, count in stats.items():
        if count > 0:
            print(f"  {category}: {count}")

if __name__ == '__main__':
    main()