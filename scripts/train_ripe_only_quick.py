#!/usr/bin/env python3
"""
Quick training of YOLOv8 model on ripe-only dataset (10 epochs for demonstration).
"""

import os
import sys
from datetime import datetime
from pathlib import Path

def train_ripe_only_quick():
    from ultralytics import YOLO
    
    # Configuration
    data_yaml = 'model/datasets/ripe_only_detection/data.yaml'
    model_size = 'yolov8s.pt'  # Using YOLOv8 small for speed and good accuracy
    epochs = 10
    imgsz = 640
    batch = 16
    workers = 4
    project = 'model/detection'
    name = f'ripe_only_yolov8s_quick_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    # Check dataset
    if not os.path.exists(data_yaml):
        print(f"Error: Dataset config not found at {data_yaml}")
        sys.exit(1)
    
    print(f"Training YOLOv8s on ripe-only dataset (quick run)")
    print(f"Data YAML: {data_yaml}")
    print(f"Model: {model_size}")
    print(f"Epochs: {epochs}")
    print(f"Image size: {imgsz}")
    print(f"Batch size: {batch}")
    print(f"Project: {project}")
    print(f"Name: {name}")
    
    # Load model
    model = YOLO(model_size)
    
    # Train
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        workers=workers,
        project=project,
        name=name,
        pretrained=True,
        seed=42,
        patience=5,
        save=True,
        save_period=5,
        val=True,
        device='0'  # Use GPU if available
    )
    
    print(f"Training completed. Results saved to {project}/{name}")
    
    # Validate
    val_results = model.val()
    print(f"Validation mAP50: {val_results.box.map50:.4f}")
    print(f"Validation mAP50-95: {val_results.box.map:.4f}")
    
    # Export to ONNX
    onnx_path = f'{project}/{name}/weights/best.onnx'
    model.export(format='onnx', imgsz=imgsz, dynamic=False)
    print(f"Model exported to ONNX: {onnx_path}")
    
    return results

if __name__ == '__main__':
    train_ripe_only_quick()