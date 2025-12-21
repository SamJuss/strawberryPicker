#!/usr/bin/env python3
"""
Update training registry with homemade model results
"""

import json
from datetime import datetime
from pathlib import Path

def update_registry():
    registry_path = Path('model/training_registry.json')
    
    # Load existing registry
    if registry_path.exists():
        with open(registry_path, 'r') as f:
            registry = json.load(f)
    else:
        registry = []
    
    # Add homemade model entry
    homemade_entry = {
        "model_id": "homemade_yolov8n_50epochs_20251219_213711",
        "model_type": "detection",
        "architecture": "yolov8n",
        "dataset": "homemade_strawberry",
        "num_classes": 1,
        "class_names": ["strawberry"],
        "training_date": "2025-12-19T21:37:11",
        "epochs": 32,
        "early_stopping": True,
        "best_epoch": 22,
        "performance": {
            "mAP50": 0.802,
            "mAP50-95": 0.47,
            "precision": 1.0,
            "recall": 0.468
        },
        "model_paths": {
            "best": "model/detection/homemade_yolov8n_50epochs2/weights/best.pt",
            "last": "model/detection/homemade_yolov8n_50epochs2/weights/last.pt"
        },
        "dataset_stats": {
            "total_images": 53,
            "train": 37,
            "val": 10,
            "test": 6,
            "data_yaml": "model/dataset_homemade_labeled/data.yaml"
        },
        "training_config": {
            "imgsz": 640,
            "batch": 8,
            "optimizer": "AdamW",
            "lr0": 0.002,
            "patience": 10,
            "mosaic": 1.0,
            "augment": True
        },
        "description": "YOLOv8n trained on homemade strawberry dataset with 53 labeled images"
    }
    
    registry.append(homemade_entry)
    
    # Save updated registry
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"Added homemade model entry to registry")
    print(f"Model ID: {homemade_entry['model_id']}")
    print(f"Performance: mAP50={homemade_entry['performance']['mAP50']:.3f}, mAP50-95={homemade_entry['performance']['mAP50-95']:.3f}")

if __name__ == '__main__':
    update_registry()