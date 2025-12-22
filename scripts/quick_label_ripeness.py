#!/usr/bin/env python3
"""
QUICK RIPENESS LABELING TOOL
Add manual labels to Kaggle ripeness dataset - just a few images
"""

import cv2
import numpy as np
from pathlib import Path
import random

class QuickRipenessLabeler:
    def __init__(self):
        """Initialize quick ripeness labeling tool"""
        self.dataset_path = Path("model/datasets/overripe_from_kaggle")
        self.output_path = Path("model/datasets/manual_ripeness_added")
        
        # Create output directories
        for split in ['train', 'val', 'test']:
            for category in ['unripe', 'ripe', 'overripe']:
                (self.output_path / 'images' / split / category).mkdir(parents=True, exist_ok=True)
                (self.output_path / 'labels' / split / category).mkdir(parents=True, exist_ok=True)
        
        self.ripeness_categories = {
            'unripe': self.dataset_path / 'unripe',
            'overripe': self.dataset_path / 'overripe'
        }
        
        print("🍓 QUICK RIPENESS LABELING TOOL")
        print("=" * 40)
        print("Perfect for adding just a few manual labels!")
        print("Categories: [1] Unripe  [2] Ripe  [3] Overripe")
        print("Controls: Click & drag to draw boxes")
        print("Press number keys to change category")
        print("Press 'S' to save and next, 'Q' to quit")
        print("=" * 40)

    def select_random_images(self, count_per_category=10):
        """Select random images from each category for quick labeling"""
        selected_images = []
        
        for category, path in self.ripeness_categories.items():
            if path.exists():
                images = list(path.glob("*.jpg"))
                if len(images) >= count_per_category:
                    selected = random.sample(images, count_per_category)
                else:
                    selected = images
                
                for img_path in selected:
                    # For unripe images, we'll mainly label them as unripe, but can find ripe ones
                    # For overripe images, we'll mainly label them as overripe, but can find ripe ones
                    suggested = 'ripe' if category == 'unripe' and random.random() > 0.7 else category
                    
                    selected_images.append({
                        'path': img_path,
                        'original_category': category,
                        'suggested_category': suggested
                    })
        
        # Shuffle for variety
        random.shuffle(selected_images)
        return selected_images

    def quick_label_image(self, image_info):
        """Quick labeling interface for a single image"""
        img_path = image_info['path']
        suggested_category = image_info['suggested_category']
        
        img = cv2.imread(str(img_path))
        if img is None:
            return None
        
        window_name = f"Quick Label: {img_path.name} (Suggested: {suggested_category})"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 600, 450)
        
        state = {
            'boxes': [],
            'current_category': suggested_category,
            'drawing': False,
            'start_pos': None,
            'current_box': None
        }
        
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                state['drawing'] = True
                state['start_pos'] = (x, y)
            elif event == cv2.EVENT_MOUSEMOVE and state['drawing']:
                state['current_box'] = (state['start_pos'][0], state['start_pos'][1], x, y)
            elif event == cv2.EVENT_LBUTTONUP:
                state['drawing'] = False
                if state['current_box']:
                    x1, y1, x2, y2 = state['current_box']
                    x1, x2 = min(x1, x2), max(x1, x2)
                    y1, y2 = min(y1, y2), max(y1, y2)
                    
                    if abs(x2 - x1) > 15 and abs(y2 - y1) > 15:  # Reasonable size
                        state['boxes'].append({
                            'bbox': [x1, y1, x2, y2],
                            'category': state['current_category']
                        })
                state['current_box'] = None
        
        cv2.setMouseCallback(window_name, mouse_callback)
        
        print(f"\n🖼️  Labeling: {img_path.name}")
        print(f"   Suggested: {suggested_category}")
        
        while True:
            display_img = img.copy()
            
            # Draw existing boxes
            for box_info in state['boxes']:
                x1, y1, x2, y2 = box_info['bbox']
                category = box_info['category']
                
                # Color coding
                colors = {'unripe': (0, 255, 0), 'ripe': (0, 255, 255), 'overripe': (0, 0, 255)}
                color = colors.get(category, (255, 255, 255))
                
                cv2.rectangle(display_img, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                cv2.putText(display_img, category, (int(x1), int(y1)-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            
            # Draw current box
            if state['current_box']:
                x1, y1, x2, y2 = state['current_box']
                cv2.rectangle(display_img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255), 1)
            
            # Show current category
            cv2.putText(display_img, f"Current: {state['current_category']}", (10, 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow(window_name, display_img)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('1'):
                state['current_category'] = 'unripe'
            elif key == ord('2'):
                state['current_category'] = 'ripe'
            elif key == ord('3'):
                state['current_category'] = 'overripe'
            elif key == ord('s') or key == ord('S'):
                cv2.destroyWindow(window_name)
                return state['boxes']
            elif key == ord('q') or key == ord('Q'):
                cv2.destroyWindow(window_name)
                return 'quit'
            elif key == 27:  # ESC
                cv2.destroyWindow(window_name)
                return None
        
        cv2.destroyWindow(window_name)
        return state['boxes']

    def save_labels(self, image_info, boxes):
        """Save labels in YOLO format"""
        if not boxes:
            return False
        
        img_path = image_info['path']
        
        # Determine final category (majority or first)
        categories = [box['category'] for box in boxes]
        final_category = categories[0] if categories else 'ripe'
        
        # Copy image to train split (80% for training)
        split = 'train' if random.random() < 0.8 else 'val'
        output_img_path = self.output_path / 'images' / split / final_category / img_path.name
        
        # Ensure directory exists
        output_img_path.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(img_path, output_img_path)
        
        # Create label file
        label_path = self.output_path / 'labels' / split / final_category / f"{img_path.stem}.txt"
        label_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to YOLO format
        img = cv2.imread(str(img_path))
        h, w = img.shape[:2]
        
        with open(label_path, 'w') as f:
            for box_info in boxes:
                x1, y1, x2, y2 = box_info['bbox']
                category = box_info['category']
                
                # Normalize coordinates
                x_center = (x1 + x2) / 2 / w
                y_center = (y1 + y2) / 2 / h
                width = (x2 - x1) / w
                height = (y2 - y1) / h
                
                # Map to class indices
                class_map = {'unripe': 0, 'ripe': 1, 'overripe': 2}
                class_idx = class_map[category]
                
                f.write(f"{class_idx} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
        
        print(f"✅ Saved {len(boxes)} labels to {final_category} ({split} split)")
        return True

    def run_quick_labeling(self, total_images=20):
        """Run quick labeling session - just a few images"""
        print(f"\n🚀 STARTING QUICK LABELING SESSION")
        print(f"Target: {total_images} images (just a few!)")
        
        # Select random images
        images_to_label = self.select_random_images(count_per_category=total_images//2)
        
        if not images_to_label:
            print("❌ No images found")
            return
        
        print(f"📊 Found {len(images_to_label)} images to label")
        
        labeled_count = 0
        skipped_count = 0
        
        for i, image_info in enumerate(images_to_label[:total_images]):
            print(f"\n📸 Image {i+1}/{min(total_images, len(images_to_label))}")
            
            boxes = self.quick_label_image(image_info)
            
            if boxes == 'quit':
                print("👋 User requested to quit")
                break
            elif boxes is None:
                skipped_count += 1
                print("⏭️  Skipped")
            elif len(boxes) == 0:
                print("⚠️  No boxes drawn")
                skipped_count += 1
            else:
                if self.save_labels(image_info, boxes):
                    labeled_count += 1
                    print(f"✅ Labeled! Total: {labeled_count}")
                else:
                    skipped_count += 1
        
        print(f"\n🎉 QUICK LABELING COMPLETE!")
        print(f"✅ Successfully labeled: {labeled_count}")
        print(f"⏭️  Skipped: {skipped_count}")
        
        # Create data.yaml
        self.create_data_yaml()
        
        return labeled_count

    def create_data_yaml(self):
        """Create data.yaml for the manual ripeness dataset"""
        data_yaml_path = self.output_path / 'data.yaml'
        
        # Count images in each split
        train_counts = {}
        val_counts = {}
        
        for category in ['unripe', 'ripe', 'overripe']:
            train_path = self.output_path / 'images' / 'train' / category
            val_path = self.output_path / 'images' / 'val' / category
            
            train_counts[category] = len(list(train_path.glob("*.jpg"))) if train_path.exists() else 0
            val_counts[category] = len(list(val_path.glob("*.jpg"))) if val_path.exists() else 0
        
        data_config = {
            'path': str(self.output_path.absolute()),
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            'nc': 3,
            'names': ['unripe', 'ripe', 'overripe'],
            'counts': {
                'train': train_counts,
                'val': val_counts
            }
        }
        
        try:
            import yaml
            with open(data_yaml_path, 'w') as f:
                yaml.dump(data_config, f, default_flow_style=False)
            print(f"✅ Created data.yaml")
        except ImportError:
            # Fallback if yaml not available
            with open(data_yaml_path, 'w') as f:
                f.write(f"path: {data_config['path']}\n")
                f.write(f"train: {data_config['train']}\n")
                f.write(f"val: {data_config['val']}\n")
                f.write(f"test: {data_config['test']}\n")
                f.write(f"nc: {data_config['nc']}\n")
                f.write("names:\n")
                for name in data_config['names']:
                    f.write(f"  - {name}\n")
            print(f"✅ Created data.yaml (manual format)")

def main():
    print("🍓 QUICK RIPENESS LABELING TOOL")
    print("Perfect for adding just a few manual labels!")
    print("This will create a multi-class ripeness detection dataset")
    
    labeler = QuickRipenessLabeler()
    
    # Quick session - just 10-20 images
    labeled = labeler.run_quick_labeling(total_images=15)
    
    if labeled > 0:
        print(f"\n🎉 SUCCESS! Added {labeled} manual ripeness labels")
        print("🚀 Next: Train a multi-class ripeness detection model")
        print("   This will enhance your robotic picker with ripeness awareness!")
    else:
        print("\n📋 No labels added this session")
        print("Run again when you're ready to add some labels!")

if __name__ == '__main__':
    main()