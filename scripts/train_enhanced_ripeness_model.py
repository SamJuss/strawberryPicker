#!/usr/bin/env python3
"""
ENHANCED RIPENESS DETECTION MODEL TRAINING
Train multi-class ripeness detection with all available categories
"""

from ultralytics import YOLO
from pathlib import Path
import yaml

def train_enhanced_ripeness_model():
    """Train enhanced ripeness detection model"""
    
    print("🍓 ENHANCED RIPENESS DETECTION MODEL TRAINING")
    print("=" * 55)
    
    # Dataset configuration
    class_names = ['overripe', 'unripe']
    
    data_config = {
        'path': 'model/datasets/complete_ripeness_combined',
        'train': 'images/train',
        'val': 'images/val', 
        'test': 'images/test',
        'nc': len(class_names),
        'names': class_names
    }
    
    # Create data.yaml
    data_path = Path("model/datasets/complete_ripeness_combined/data.yaml")
    data_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(data_path, 'w') as f:
        yaml.dump(data_config, f, default_flow_style=False)
    
    print("✅ Created enhanced ripeness dataset configuration")
    print(f"📊 Classes: {len(class_names)}")
    for i, name in enumerate(class_names):
        print(f"   Class {i}: {name}")
    
    print("\n🚀 Ready to train enhanced ripeness detection model!")
    print("Suggested training commands:")
    print("  yolo train data=model/datasets/complete_ripeness_combined/data.yaml model=yolov8n.pt epochs=100 imgsz=640")
    print("  yolo train data=model/datasets/complete_ripeness_combined/data.yaml model=yolov8s.pt epochs=100 imgsz=640")

if __name__ == '__main__':
    import yaml
    train_enhanced_ripeness_model()