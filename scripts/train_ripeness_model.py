#!/usr/bin/env python3
"""
TRAIN RIPENESS DETECTION MODEL
Train multi-class ripeness detection after manual labeling
"""

from ultralytics import YOLO
from pathlib import Path

def train_ripeness_model():
    """Train ripeness detection model"""
    
    print("🍓 TRAINING RIPENESS DETECTION MODEL")
    print("=" * 45)
    
    # Dataset configuration
    data_yaml = """
path: model/datasets/manual_ripeness_combined
train: images/train
val: images/val
test: images/test

nc: 3
names: ['ripe', 'unripe', 'overripe']
"""
    
    # Save data.yaml
    data_path = Path("model/datasets/manual_ripeness_combined/data.yaml")
    data_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(data_path, 'w') as f:
        f.write(data_yaml.strip())
    
    print("✅ Created ripeness dataset configuration")
    print("📊 Classes:")
    print("   0: ripe (your manual labels)")
    print("   1: unripe (from Kaggle)")
    print("   2: overripe (from Kaggle)")
    
    print("\n🚀 Ready to train ripeness detection model!")
    print("Run: yolo train data=model/datasets/manual_ripeness_combined/data.yaml model=yolov8n.pt epochs=50")

if __name__ == '__main__':
    train_ripeness_model()
