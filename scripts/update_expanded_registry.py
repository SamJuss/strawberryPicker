#!/usr/bin/env python3
"""
Update training registry with expanded homemade model results
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
    
    # Add expanded model entry
    expanded_entry = {
        "model_id": "homemade_yolov8n_100epochs_expanded_20251219_220812",
        "model_type": "detection",
        "architecture": "yolov8n",
        "dataset": "homemade_strawberry_expanded",
        "num_classes": 1,
        "class_names": ["strawberry"],
        "training_date": "2025-12-19T22:08:12",
        "epochs": 100,
        "early_stopping": False,
        "best_epoch": 100,
        "performance": {
            "mAP50": 0.977,
            "mAP50-95": 0.666,
            "precision": 0.984,
            "recall": 0.966
        },
        "model_paths": {
            "best": "model/detection/homemade_yolov8n_100epochs_expanded/weights/best.pt",
            "last": "model/detection/homemade_yolov8n_100epochs_expanded/weights/last.pt"
        },
        "dataset_stats": {
            "total_images": 106,
            "labeled_images": 95,
            "train": 66,
            "val": 19,
            "test": 10,
            "data_yaml": "model/dataset_homemade_labeled/data.yaml"
        },
        "training_config": {
            "imgsz": 640,
            "batch": 8,
            "optimizer": "AdamW",
            "lr0": 0.002,
            "patience": 0,
            "mosaic": 1.0,
            "augment": True,
            "close_mosaic": 10
        },
        "improvement_over_previous": {
            "previous_model": "homemade_yolov8n_50epochs_20251219_213711",
            "mAP50_gain": 0.175,
            "recall_gain": 0.498,
            "dataset_increase": 79,
            "epochs_increase": 68
        },
        "description": "YOLOv8n trained on expanded homemade dataset (95 labeled images, 100 epochs). Massive improvement in recall (+106%) and mAP@50 (+22%)."
    }
    
    registry.append(expanded_entry)
    
    # Save updated registry
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"Added expanded homemade model entry to registry")
    print(f"Model ID: {expanded_entry['model_id']}")
    print(f"Performance: mAP50={expanded_entry['performance']['mAP50']:.3f}, mAP50-95={expanded_entry['performance']['mAP50-95']:.3f}")
    print(f"Recall: {expanded_entry['performance']['recall']:.3f} (+{expanded_entry['improvement_over_previous']['recall_gain']:.1%} vs previous)")

if __name__ == '__main__':
    update_registry()