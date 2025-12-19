#!/usr/bin/env python3
"""
Train a YOLOv8n model on ripe-only dataset for 5 epochs and evaluate.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

def train_and_evaluate():
    from ultralytics import YOLO
    
    # Configuration
    data_yaml = 'model/datasets/ripe_only_detection/data.yaml'
    model_size = 'yolov8n.pt'  # Using YOLOv8 nano for speed
    epochs = 5
    imgsz = 640
    batch = 16
    workers = 4
    project = 'model/detection'
    name = f'ripe_only_yolov8n_quick_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    # Check dataset
    if not os.path.exists(data_yaml):
        print(f"Error: Dataset config not found at {data_yaml}")
        sys.exit(1)
    
    print(f"Training YOLOv8n on ripe-only dataset (quick run)")
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
        patience=3,
        save=True,
        save_period=1,
        val=True,
        device='0'  # Use GPU if available
    )
    
    print(f"Training completed. Results saved to {project}/{name}")
    
    # Validate
    val_results = model.val()
    print(f"Validation mAP50: {val_results.box.map50:.4f}")
    print(f"Validation mAP50-95: {val_results.box.map:.4f}")
    
    # Save metrics to a file
    metrics_path = Path(project) / name / 'metrics.txt'
    with open(metrics_path, 'w') as f:
        f.write(f"mAP50: {val_results.box.map50:.4f}\n")
        f.write(f"mAP50-95: {val_results.box.map:.4f}\n")
        f.write(f"Precision: {val_results.box.p:.4f}\n")
        f.write(f"Recall: {val_results.box.r:.4f}\n")
    
    print(f"Metrics saved to {metrics_path}")
    
    # Export to ONNX
    onnx_path = f'{project}/{name}/weights/best.onnx'
    model.export(format='onnx', imgsz=imgsz, dynamic=False)
    print(f"Model exported to ONNX: {onnx_path}")
    
    return model, val_results

if __name__ == '__main__':
    train_and_evaluate()