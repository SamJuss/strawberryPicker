#!/usr/bin/env python3
"""
Train YOLOv8 model on homemade strawberry dataset
"""

from ultralytics import YOLO
import os
from pathlib import Path

def train_homemade_model():
    """Train YOLOv8n on homemade dataset"""
    
    # Create output directory
    os.makedirs('model/detection', exist_ok=True)
    
    print("="*60)
    print("TRAINING YOLOV8N ON EXPANDED HOMEMADE DATASET")
    print("="*60)
    print(f"Dataset: model/dataset_homemade_labeled/data.yaml")
    print(f"Model: YOLOv8n")
    print(f"Epochs: 100 (no early stopping)")
    print("="*60)
    
    # Load pretrained model
    model = YOLO('yolov8n.pt')
    
    # Train with more epochs and no early stopping
    results = model.train(
        data='model/dataset_homemade_labeled/data.yaml',
        epochs=100,
        imgsz=640,
        batch=8,
        name='homemade_yolov8n_100epochs_expanded',
        project='model/detection',
        patience=0,  # Disable early stopping
        save=True,
        save_period=10,
        cache=True,
        device=0  # Use GPU if available
    )
    
    print("\n" + "="*60)
    print("TRAINING COMPLETED!")
    print("="*60)
    print(f"Best model saved at: model/detection/homemade_yolov8n_50epochs/weights/best.pt")
    print(f"Results saved in: model/detection/homemade_yolov8n_50epochs/")
    print("="*60)
    
    return results

if __name__ == '__main__':
    train_homemade_model()