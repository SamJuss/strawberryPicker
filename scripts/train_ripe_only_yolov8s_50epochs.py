#!/usr/bin/env python3
"""
Train a YOLOv8s model on ripe-only dataset for 50 epochs with early stopping.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

def train_and_evaluate():
    from ultralytics import YOLO
    
    # Configuration
    data_yaml = 'model/datasets/ripe_only_detection/data.yaml'
    model_size = 'yolov8s.pt'  # Using YOLOv8 small for balance of speed and accuracy
    epochs = 50
    imgsz = 640
    batch = 8  # Reduced batch size to avoid memory issues
    workers = 4
    project = 'model/detection'
    name = f'ripe_only_yolov8s_50epochs_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    # Check dataset
    if not os.path.exists(data_yaml):
        print(f"Error: Dataset config not found at {data_yaml}")
        sys.exit(1)
    
    print(f"Training YOLOv8s on ripe-only dataset (50 epochs)")
    print(f"Data YAML: {data_yaml}")
    print(f"Model: {model_size}")
    print(f"Epochs: {epochs}")
    print(f"Image size: {imgsz}")
    print(f"Batch size: {batch}")
    print(f"Project: {project}")
    print(f"Name: {name}")
    
    # Load model
    model = YOLO(model_size)
    
    # Train with improved hyperparameters
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
        patience=10,  # Early stopping patience
        save=True,
        save_period=5,
        val=True,
        device='0',  # Use GPU if available
        # Augmentation
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10.0,
        translate=0.1,
        scale=0.5,
        shear=2.0,
        perspective=0.001,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1,
        copy_paste=0.1,
        # Optimization
        lr0=0.01,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3.0,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        box=7.5,
        cls=0.5,
        dfl=1.5,
        # Additional
        close_mosaic=10,
        amp=True,  # Mixed precision
        dropout=0.0,
        verbose=True
    )
    
    print(f"Training completed. Results saved to {project}/{name}")
    
    # Validate
    val_results = model.val()
    print(f"Validation mAP50: {val_results.box.map50:.4f}")
    print(f"Validation mAP50-95: {val_results.box.map:.4f}")
    # Precision and recall are arrays, take mean
    if hasattr(val_results.box, 'p'):
        precision = val_results.box.p.mean() if hasattr(val_results.box.p, 'mean') else val_results.box.p
        recall = val_results.box.r.mean() if hasattr(val_results.box.r, 'mean') else val_results.box.r
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
    
    # Save metrics to a file
    metrics_path = Path(project) / name / 'metrics.txt'
    with open(metrics_path, 'w') as f:
        f.write(f"mAP50: {val_results.box.map50:.4f}\n")
        f.write(f"mAP50-95: {val_results.box.map:.4f}\n")
        if hasattr(val_results.box, 'p'):
            f.write(f"Precision: {precision:.4f}\n")
            f.write(f"Recall: {recall:.4f}\n")
    
    print(f"Metrics saved to {metrics_path}")
    
    # Export to ONNX
    onnx_path = f'{project}/{name}/weights/best.onnx'
    model.export(format='onnx', imgsz=imgsz, dynamic=False)
    print(f"Model exported to ONNX: {onnx_path}")
    
    return model, val_results

if __name__ == '__main__':
    train_and_evaluate()