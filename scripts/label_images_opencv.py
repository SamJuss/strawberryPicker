#!/usr/bin/env python3
"""
Simple OpenCV-based image labeling tool for WSL/Linux.
Works reliably without Qt dependencies.

Usage:
    python scripts/label_images_opencv.py model/dataset_homemade

Controls:
- Left click and drag: Draw bounding box
- 's': Save current image labels and move to next
- 'n': Skip current image (no save)
- 'q': Quit without saving current image
- 'r': Reset boxes for current image
- 'd': Delete last box
"""

import cv2
import os
import sys
from pathlib import Path
import numpy as np

class ImageLabeler:
    def __init__(self, image_dir, class_names):
        self.image_dir = Path(image_dir)
        self.class_names = class_names
        self.class_id = 0
        
        # Get all images
        self.image_files = sorted([f for f in self.image_dir.glob('*.jpg') 
                                   if not f.name.endswith(':Zone.Identifier')])
        
        if not self.image_files:
            print(f"No JPG images found in {image_dir}")
            sys.exit(1)
        
        print(f"Found {len(self.image_files)} images to label")
        
        # State variables
        self.current_idx = 0
        self.boxes = []  # List of (x1, y1, x2, y2)
        self.drawing = False
        self.start_point = None
        self.current_image = None
        self.original_image = None
        
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                # Create a copy of the image to draw the temporary box
                self.current_image = self.original_image.copy()
                cv2.rectangle(self.current_image, self.start_point, (x, y), (0, 255, 0), 2)
                self.draw_boxes()
                
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            if self.start_point:
                # Add the completed box
                x1, y1 = self.start_point
                x2, y2 = x, y
                
                # Ensure coordinates are valid (x1 < x2, y1 < y2)
                x1, x2 = min(x1, x2), max(x1, x2)
                y1, y2 = min(y1, y2), max(y1, y2)
                
                # Only add if box has non-zero area
                if x2 > x1 and y2 > y1:
                    self.boxes.append((x1, y1, x2, y2))
                
                self.start_point = None
                self.redraw_image()
    
    def draw_boxes(self):
        """Draw all saved boxes on the current image"""
        if self.current_image is None:
            return
        
        for i, (x1, y1, x2, y2) in enumerate(self.boxes):
            color = (0, 255, 0) if i == len(self.boxes) - 1 else (255, 0, 0)
            cv2.rectangle(self.current_image, (x1, y1), (x2, y2), color, 2)
            cv2.putText(self.current_image, f"{self.class_names[self.class_id]} {i+1}", 
                       (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    def redraw_image(self):
        """Redraw the image with all boxes"""
        self.current_image = self.original_image.copy()
        self.draw_boxes()
    
    def save_labels(self, image_file):
        """Save labels in YOLO format"""
        if not self.boxes:
            # No objects to label, create empty file or skip
            return True
        
        # Get image dimensions
        height, width = self.original_image.shape[:2]
        
        # Create label file path
        label_file = image_file.with_suffix('.txt')
        
        with open(label_file, 'w') as f:
            for x1, y1, x2, y2 in self.boxes:
                # Convert to YOLO format (normalized coordinates)
                x_center = ((x1 + x2) / 2) / width
                y_center = ((y1 + y2) / 2) / height
                box_width = (x2 - x1) / width
                box_height = (y2 - y1) / height
                
                # Write in YOLO format: class_id x_center y_center width height
                f.write(f"{self.class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}\n")
        
        print(f"Saved {len(self.boxes)} boxes to {label_file}")
        return True
    
    def load_image(self, idx):
        """Load and display an image"""
        if idx >= len(self.image_files):
            return False
        
        image_file = self.image_files[idx]
        print(f"\nLoading image {idx + 1}/{len(self.image_files)}: {image_file.name}")
        
        # Load image
        self.original_image = cv2.imread(str(image_file))
        if self.original_image is None:
            print(f"Error: Could not load image {image_file}")
            return False
        
        self.redraw_image()
        self.boxes = []
        
        # Check if label file already exists
        label_file = image_file.with_suffix('.txt')
        if label_file.exists():
            print(f"Found existing labels: {label_file.name}")
            # Could load existing boxes here if needed
        
        return True
    
    def run(self):
        """Main labeling loop"""
        # Create window
        cv2.namedWindow('Image Labeler', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Image Labeler', self.mouse_callback)
        
        # Load first image
        if not self.load_image(self.current_idx):
            return
        
        print("\n" + "="*60)
        print("CONTROLS:")
        print("  - Left click + drag: Draw bounding box")
        print("  - 's': Save and next image")
        print("  - 'n': Skip to next image (no save)")
        print("  - 'q': Quit")
        print("  - 'r': Reset all boxes")
        print("  - 'd': Delete last box")
        print("="*60)
        
        while True:
            # Display image
            cv2.imshow('Image Labeler', self.current_image)
            
            # Wait for key press
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('s'):  # Save and next
                self.save_labels(self.image_files[self.current_idx])
                self.current_idx += 1
                if not self.load_image(self.current_idx):
                    print("All images labeled!")
                    break
            
            elif key == ord('n'):  # Skip to next
                self.current_idx += 1
                if not self.load_image(self.current_idx):
                    print("All images labeled!")
                    break
            
            elif key == ord('q'):  # Quit
                print("Quitting without saving current image...")
                break
            
            elif key == ord('r'):  # Reset boxes
                self.boxes = []
                self.redraw_image()
                print(f"Reset all boxes (total: {len(self.boxes)})")
            
            elif key == ord('d'):  # Delete last box
                if self.boxes:
                    self.boxes.pop()
                    self.redraw_image()
                    print(f"Deleted last box (total: {len(self.boxes)})")
                else:
                    print("No boxes to delete")
            
            elif key == ord('c'):  # Print current box count
                print(f"Current boxes: {len(self.boxes)}")
        
        cv2.destroyAllWindows()
        print(f"\nLabeling complete! Labeled {self.current_idx} images.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python label_images_opencv.py <image_directory>")
        sys.exit(1)
    
    image_dir = sys.argv[1]
    class_names = ['strawberry']
    
    labeler = ImageLabeler(image_dir, class_names)
    labeler.run()

if __name__ == '__main__':
    main()