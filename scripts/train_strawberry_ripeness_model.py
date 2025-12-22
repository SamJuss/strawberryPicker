#!/usr/bin/env python3
"""
STRAWBERRY RIPENESS DETECTION MODEL TRAINING
Train multi-class ripeness detection specifically for strawberries
"""

from ultralytics import YOLO
from pathlib import Path
import yaml

def train_strawberry_ripeness_model():
    """Train strawberry ripeness detection model"""
    
    print("🍓 STRAWBERRY RIPENESS DETECTION MODEL TRAINING")
    print("=" * 60)
    
    # Dataset configuration
    class_names = ['overripe', 'ripe', 'unripe']
    
    data_config = {
        'path': 'model/datasets/strawberry_ripeness_combined',
        'train': 'images/train',
        'val': 'images/val', 
        'test': 'images/test',
        'nc': len(class_names),
        'names': class_names
    }
    
    # Save data.yaml
    data_path = Path("model/datasets/strawberry_ripeness_combined/data.yaml")
    data_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(data_path, 'w') as f:
        yaml.dump(data_config, f, default_flow_style=False)
    
    print("✅ Created strawberry ripeness dataset configuration")
    print(f"📊 Classes: {len(class_names)}")
    for i, name in enumerate(class_names):
        print(f"   Class {i}: {name}")
    
    print("\n🚀 Ready to train strawberry ripeness detection model!")
    print("Suggested training commands:")
    print("  yolo train data=model/datasets/strawberry_ripeness_combined/data.yaml model=yolov8n.pt epochs=100 imgsz=640")
    print("  yolo train data=model/datasets/strawberry_ripeness_combined/data.yaml model=yolov8s.pt epochs=100 imgsz=640")
    
    print("\n🎯 This model will give your robotic picker the intelligence to:")
    print("  ✅ Detect ripe strawberries for harvesting")
    print("  ✅ Avoid unripe strawberries (wait for ripening)")
    print("  ✅ Avoid overripe strawberries (prevent waste)")
    print("  ✅ Optimize harvest timing for maximum quality!")

if __name__ == '__main__':
    import yaml
    train_strawberry_ripeness_model()