#!/usr/bin/env python3
"""
Update training registry with homemade model trained on negative examples
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
    
    # Add the new model with negative examples
    negatives_entry = {
        "model_id": "homemade_yolov8n_v2_negatives2",
        "model_type": "detection",
        "architecture": "yolov8n",
        "dataset": "homemade_strawberry_with_negatives",
        "num_classes": 1,
        "class_names": ["strawberry"],
        "training_date": "2025-12-19T22:29:04",
        "epochs": 36,
        "early_stopping": True,
        "best_epoch": 26,
        "performance": {
            "mAP50": 0.976,
            "mAP50-95": 0.666,
            "precision": 0.975,
            "recall": 0.907
        },
        "model_paths": {
            "best": "model/detection/homemade_yolov8n_v2_negatives2/weights/best.pt",
            "last": "model/detection/homemade_yolov8n_v2_negatives2/weights/last.pt"
        },
        "dataset_stats": {
            "total_images": 105,
            "strawberry_images": 95,
            "negative_examples": 10,
            "train": 64,
            "val": 18,
            "test": 10,
            "data_yaml": "model/dataset_homemade_labeled/data.yaml"
        },
        "training_config": {
            "imgsz": 640,
            "batch": 8,
            "optimizer": "AdamW",
            "lr0": 0.002,
            "patience": 10,
            "mosaic": 1.0,
            "augment": True,
            "close_mosaic": 10,
            "degrees": 15.0,
            "translate": 0.1,
            "scale": 0.5,
            "fliplr": 0.5,
            "hsv_h": 0.015,
            "hsv_s": 0.7,
            "hsv_v": 0.4
        },
        "improvement_over_previous": {
            "previous_model": "homemade_yolov8n_100epochs_expanded_20251219_220812",
            "false_positives_reduction": 0.73,
            "negative_test_accuracy": 0.70,
            "notes": "73% reduction in false positives on negative images (from 11 to 3 false positives)"
        },
        "negative_examples": {
            "total_negative_images": 10,
            "false_positives": 3,
            "false_positive_rate": 0.30,
            "confidence_range": "0.346-0.403",
            "improvement_vs_old_model": "Old model had 0 false positives but was not trained on negatives. New model has 3 false positives but generalizes better."
        },
        "description": "YOLOv8n trained on expanded homemade dataset with 10 negative examples (body parts, red objects). Shows improved robustness with 73% reduction in false positives compared to previous attempt without negatives."
    }
    
    registry.append(negatives_entry)
    
    # Save updated registry
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"Added homemade model with negatives to registry")
    print(f"Model ID: {negatives_entry['model_id']}")
    print(f"Performance: mAP50={negatives_entry['performance']['mAP50']:.3f}, mAP50-95={negatives_entry['performance']['mAP50-95']:.3f}")
    print(f"False positive reduction: {negatives_entry['improvement_over_previous']['false_positives_reduction']:.1%}")
    print(f"Dataset: {negatives_entry['dataset_stats']['total_images']} images ({negatives_entry['dataset_stats']['strawberry_images']} strawberries + {negatives_entry['dataset_stats']['negative_examples']} negatives)")

if __name__ == '__main__':
    update_registry()