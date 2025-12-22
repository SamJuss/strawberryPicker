#!/usr/bin/env python3
"""
MANUAL RIPENESS DATASET LABELING TOOL
Label strawberries with ripeness levels for enhanced detection
"""

import cv2
import numpy as np
from pathlib import Path
import json
import shutil
from datetime import datetime
import argparse

class RipenessLabelingTool:
    def __init__(self, dataset_path="model/datasets/overripe_from_kaggle"):
        """
        Initialize ripeness labeling tool for Kaggle dataset
        
        Args:
            dataset_path: Path to the overripe_from_kaggle dataset
        """
        self.dataset_path = Path(dataset_path)
        self.ripeness_categories = {
            'unripe': 'model/datasets/overripe_from_kaggle/unripe',
            'overripe': 'model/datasets/overripe_from_kaggle/overripe'
        }
        
        # Create output directories for manual labels
        self.manual_output = Path("model/datasets/manual_ripeness_labeled")
        self.manual_output.mkdir(parents=True, exist_ok=True)
        
        for category in ['unripe', 'ripe', 'overripe']:
            (self.manual_output / 'images' / category).mkdir(parents=True, exist_ok=True)
            (self.manual_output / 'labels' / category).mkdir(parents=True, exist_ok=True)
        
        self.current_category = None
        self.current_image_idx = 0
        self.images_to_label = []
        self.labels = {}
        
        print("🍓 RIPENESS DATASET LABELING TOOL")
        print("=" * 50)
        print("Categories: [1] Unripe  [2] Ripe  [3] Overripe  [S] Skip  [Q] Quit")
        print("Instructions:")
        print("- Click and drag to draw bounding boxes")
        print("- Press number keys to assign ripeness category")
        print("- Press 'S' to skip difficult images")
        print("- Press 'Q' to save and quit")
        print("=" * 50)

    def prepare_labeling_list(self, max_per_category=100):
        """
        Prepare list of images for manual labeling
        
        Args:
            max_per_category: Maximum images to label per category
        """
        self.images_to_label = []
        
        for category, path in self.ripeness_categories.items():
            category_path = Path(path)
            if category_path.exists():
                images = list(category_path.glob("*.jpg"))[:max_per_category]
                for img_path in images:
                    self.images_to_label.append({
                        'path': img_path,
                        'original_category': category,
                        'suggested_category': 'ripe' if category == 'unripe' else category
                    })
        
        print(f"📊 Prepared {len(self.images_to_label)} images for labeling")
        print(f"   - Unripe images: {len([img for img in self.images_to_label if img['original_category'] == 'unripe'])}")
        print(f"   - Overripe images: {len([img for img in self.images_to_label if img['original_category'] == 'overripe'])}")
        
        return self.images_to_label

    def label_image(self, image_info):
        """
        Label a single image with ripeness detection
        
        Args:
            image_info: Dictionary with image path and category info
        """
        img_path = image_info['path']
        original_category = image_info['original_category']
        suggested_category = image_info['suggested_category']
        
        # Load image
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"❌ Could not load image: {img_path}")
            return None
        
        # Create window for labeling
        window_name = f"Label Ripeness - {img_path.name} (Suggested: {suggested_category})"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 600)
        
        # Store drawing state
        drawing_state = {
            'drawing': False,
            'start_x': -1,
            'start_y': -1,
            'current_box': None,
            'boxes': [],
            'current_category': suggested_category
        }
        
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                drawing_state['drawing'] = True
                drawing_state['start_x'], drawing_state['start_y'] = x, y
            elif event == cv2.EVENT_MOUSEMOVE:
                if drawing_state['drawing']:
                    drawing_state['current_box'] = (drawing_state['start_x'], drawing_state['start_y'], x, y)
            elif event == cv2.EVENT_LBUTTONUP:
                drawing_state['drawing'] = False
                if drawing_state['current_box']:
                    x1, y1, x2, y2 = drawing_state['current_box']
                    # Ensure proper ordering
                    x1, x2 = min(x1, x2), max(x1, x2)
                    y1, y2 = min(y1, y2), max(y1, y2)
                    
                    # Only add if box is reasonable size
                    if abs(x2 - x1) > 20 and abs(y2 - y1) > 20:
                        drawing_state['boxes'].append({
                            'bbox': [x1, y1, x2, y2],
                            'category': drawing_state['current_category']
                        })
                        print(f"✅ Added {drawing_state['current_category']} box: [{x1}, {y1}, {x2}, {y2}]")
                drawing_state['current_box'] = None
        
        cv2.setMouseCallback(window_name, mouse_callback)
        
        print(f"\n🖼️  Labeling: {img_path.name}")
        print(f"   Original category: {original_category}")
        print(f"   Suggested: {suggested_category}")
        print("   Draw boxes around strawberries and press number keys to change category")
        
        while True:
            # Create display image
            display_img = img.copy()
            
            # Draw existing boxes
            for box_info in drawing_state['boxes']:
                x1, y1, x2, y2 = box_info['bbox']
                category = box_info['category']
                
                # Color coding for categories
                if category == 'unripe':
                    color = (0, 255, 0)  # Green
                elif category == 'ripe':
                    color = (0, 255, 255)  # Yellow
                else:  # overripe
                    color = (0, 0, 255)  # Red
                
                cv2.rectangle(display_img, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                cv2.putText(display_img, category, (int(x1), int(y1)-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw current box being drawn
            if drawing_state['current_box']:
                x1, y1, x2, y2 = drawing_state['current_box']
                cv2.rectangle(display_img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255), 2)
            
            # Show current category
            cv2.putText(display_img, f"Current: {drawing_state['current_category']}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            cv2.imshow(window_name, display_img)
            
            key = cv2.waitKey(1) & 0xFF
            
            # Handle key presses
            if key == ord('1'):
                drawing_state['current_category'] = 'unripe'
                print("🟢 Switched to unripe labeling")
            elif key == ord('2'):
                drawing_state['current_category'] = 'ripe'
                print("🟡 Switched to ripe labeling")
            elif key == ord('3'):
                drawing_state['current_category'] = 'overripe'
                print("🔴 Switched to overripe labeling")
            elif key == ord('s') or key == ord('S'):
                print("⏭️  Skipping this image")
                cv2.destroyWindow(window_name)
                return None
            elif key == ord('q') or key == ord('Q'):
                print("💾 Saving labels and quitting...")
                cv2.destroyWindow(window_name)
                return drawing_state['boxes']
            elif key == 27:  # ESC key
                print("❌ Canceling without saving")
                cv2.destroyWindow(window_name)
                return None
        
        cv2.destroyWindow(window_name)
        return drawing_state['boxes']

    def save_labels(self, image_info, boxes):
        """
        Save labels in YOLO format
        
        Args:
            image_info: Image information
            boxes: List of bounding boxes with categories
        """
        if not boxes:
            return False
        
        img_path = image_info['path']
        original_category = image_info['original_category']
        
        # Determine output category based on majority of labels or original
        categories = [box['category'] for box in boxes]
        final_category = max(set(categories), key=categories.count) if categories else original_category
        
        # Copy image to appropriate category
        output_img_path = self.manual_output / 'images' / final_category / img_path.name
        shutil.copy2(img_path, output_img_path)
        
        # Create label file
        label_path = self.manual_output / 'labels' / final_category / f"{img_path.stem}.txt"
        
        # Convert to YOLO format
        img = cv2.imread(str(img_path))
        h, w = img.shape[:2]
        
        with open(label_path, 'w') as f:
            for box_info in boxes:
                x1, y1, x2, y2 = box_info['bbox']
                category = box_info['category']
                
                # Convert to YOLO format (normalized coordinates)
                x_center = (x1 + x2) / 2 / w
                y_center = (y1 + y2) / 2 / h
                width = (x2 - x1) / w
                height = (y2 - y1) / h
                
                # Map category to class index
                class_map = {'unripe': 0, 'ripe': 1, 'overripe': 2}
                class_idx = class_map[category]
                
                f.write(f"{class_idx} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
        
        print(f"✅ Saved {len(boxes)} labels to {label_path}")
        return True

    def create_data_yaml(self):
        """Create data.yaml for the manual ripeness dataset"""
        data_yaml_path = self.manual_output / 'data.yaml'
        
        data_config = {
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            'nc': 3,
            'names': ['unripe', 'ripe', 'overripe']
        }
        
        with open(data_yaml_path, 'w') as f:
            yaml.dump(data_config, f, default_flow_style=False)
        
        print(f"✅ Created data.yaml at {data_yaml_path}")

    def run_labeling_session(self, max_images=50):
        """
        Run a complete labeling session
        
        Args:
            max_images: Maximum number of images to label in this session
        """
        print(f"\n🚀 STARTING RIPENESS LABELING SESSION")
        print(f"Target: {max_images} images")
        
        # Prepare labeling list
        images_to_label = self.prepare_labeling_list(max_per_category=max_images//2)
        
        if not images_to_label:
            print("❌ No images found for labeling")
            return
        
        # Shuffle for variety
        import random
        random.shuffle(images_to_label)
        
        labeled_count = 0
        skipped_count = 0
        
        for i, image_info in enumerate(images_to_label[:max_images]):
            print(f"\n📸 Processing image {i+1}/{min(max_images, len(images_to_label))}")
            
            boxes = self.label_image(image_info)
            
            if boxes is None:
                skipped_count += 1
                print("⏭️  Skipped this image")
            elif len(boxes) == 0:
                print("⚠️  No boxes drawn - skipping save")
                skipped_count += 1
            else:
                if self.save_labels(image_info, boxes):
                    labeled_count += 1
                    print(f"✅ Successfully labeled image {labeled_count}")
                else:
                    skipped_count += 1
        
        print(f"\n🎉 LABELING SESSION COMPLETE!")
        print(f"✅ Labeled images: {labeled_count}")
        print(f"⏭️  Skipped images: {skipped_count}")
        
        # Create data.yaml
        self.create_data_yaml()
        
        return labeled_count

def main():
    parser = argparse.ArgumentParser(description='Manual Ripeness Dataset Labeling Tool')
    parser.add_argument('--max-images', type=int, default=50, help='Maximum images to label')
    parser.add_argument('--dataset-path', type=str, default='model/datasets/overripe_from_kaggle', 
                       help='Path to ripeness dataset')
    
    args = parser.parse_args()
    
    tool = RipenessLabelingTool(args.dataset_path)
    labeled_count = tool.run_labeling_session(args.max_images)
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Review labeled images in: {tool.manual_output}")
    print(f"2. Train ripeness detection model using the new labels")
    print(f"3. Combine with existing manual strawberry detection")
    print(f"4. Deploy multi-class ripeness-aware detector")

if __name__ == '__main__':
    import yaml
    main()