#!/usr/bin/env python3
"""
Update training_registry.json with new ripe-only models trained without early stopping.
"""

import json
import os
from datetime import datetime

def main():
    registry_path = 'model/training_registry.json'
    
    # Read existing registry
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    # Model 1: YOLOv8n no early stop
    model_n_path = 'model/detection/ripe_only_yolov8n_no_early_stop_20251219_143448'
    metrics_n_path = os.path.join(model_n_path, 'metrics.txt')
    args_n_path = os.path.join(model_n_path, 'args.yaml')
    
    if os.path.exists(metrics_n_path):
        with open(metrics_n_path, 'r') as f:
            lines = f.readlines()
            metrics = {}
            for line in lines:
                if ':' in line:
                    key, val = line.strip().split(': ', 1)
                    metrics[key] = float(val) if '.' in val else val
    else:
        metrics = {}
    
    entry_n = {
        "run_id": f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_yolov8n_ripe_no_early_stop",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "experiment_name": "ripe_only_yolov8n_no_early_stop",
        "model_type": "detection",
        "model_architecture": "YOLOv8",
        "model_size": "n",
        "pretrained": True,
        "dataset_name": "ripe_only_detection",
        "dataset_size": 629,
        "num_classes": 1,
        "class_names": ["ripe"],
        "batch_size": 16,
        "image_size": 640,
        "epochs_planned": 50,
        "epochs_completed": 50,
        "learning_rate": 0.002,  # from args.yaml optimizer auto determined
        "optimizer": "AdamW",
        "weight_decay": 0.0005,
        "train_loss": None,  # not recorded in metrics
        "val_loss": None,
        "precision": metrics.get("Precision", 0.0),
        "recall": metrics.get("Recall", 0.0),
        "mAP50": metrics.get("mAP50", 0.0),
        "mAP50_95": metrics.get("mAP50-95", 0.0),
        "training_time_minutes": 0.142 * 60,  # 0.142 hours from logs
        "early_stopped": False,
        "best_epoch": 50,
        "gpu_name": "NVIDIA GeForce RTX 3050 Ti Laptop GPU",
        "gpu_memory_peak_gb": 1.96,  # approximate from logs
        "cpu_count": 20,
        "ram_total_gb": 15.47,
        "python_version": "3.12.3",
        "pytorch_version": "2.9.1+cu128",
        "cuda_version": "12.8",
        "os_info": "linux",
        "model_path": os.path.join(model_n_path, "weights/best.pt"),
        "results_path": model_n_path,
        "config_path": args_n_path,
        "status": "completed",
        "notes": "Trained for 50 epochs without early stopping on ripe-only dataset. Patience=0.",
        "tensorflow_version": "N/A",
        "f1_score": None,
        "validation": {
            "inference_time_s": 0.0058  # from validation logs
        }
    }
    
    # Model 2: YOLOv8s no early stop
    model_s_path = 'model/detection/ripe_only_yolov8s_no_early_stop_20251219_144510'
    metrics_s_path = os.path.join(model_s_path, 'metrics.txt')
    args_s_path = os.path.join(model_s_path, 'args.yaml')
    
    if os.path.exists(metrics_s_path):
        with open(metrics_s_path, 'r') as f:
            lines = f.readlines()
            metrics_s = {}
            for line in lines:
                if ':' in line:
                    key, val = line.strip().split(': ', 1)
                    metrics_s[key] = float(val) if '.' in val else val
    else:
        metrics_s = {}
    
    entry_s = {
        "run_id": f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_yolov8s_ripe_no_early_stop",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "experiment_name": "ripe_only_yolov8s_no_early_stop",
        "model_type": "detection",
        "model_architecture": "YOLOv8",
        "model_size": "s",
        "pretrained": True,
        "dataset_name": "ripe_only_detection",
        "dataset_size": 629,
        "num_classes": 1,
        "class_names": ["ripe"],
        "batch_size": 8,
        "image_size": 640,
        "epochs_planned": 50,
        "epochs_completed": 50,
        "learning_rate": 0.002,
        "optimizer": "AdamW",
        "weight_decay": 0.0005,
        "train_loss": None,
        "val_loss": None,
        "precision": metrics_s.get("Precision", 0.0),
        "recall": metrics_s.get("Recall", 0.0),
        "mAP50": metrics_s.get("mAP50", 0.0),
        "mAP50_95": metrics_s.get("mAP50-95", 0.0),
        "training_time_minutes": 0.277 * 60,  # 0.277 hours from logs
        "early_stopped": False,
        "best_epoch": 50,
        "gpu_name": "NVIDIA GeForce RTX 3050 Ti Laptop GPU",
        "gpu_memory_peak_gb": 1.96,
        "cpu_count": 20,
        "ram_total_gb": 15.47,
        "python_version": "3.12.3",
        "pytorch_version": "2.9.1+cu128",
        "cuda_version": "12.8",
        "os_info": "linux",
        "model_path": os.path.join(model_s_path, "weights/best.pt"),
        "results_path": model_s_path,
        "config_path": args_s_path,
        "status": "completed",
        "notes": "Trained for 50 epochs without early stopping on ripe-only dataset. Patience=0.",
        "tensorflow_version": "N/A",
        "f1_score": None,
        "validation": {
            "inference_time_s": 0.0104  # from validation logs
        }
    }
    
    # Insert at the beginning of the registry (most recent first)
    registry.insert(0, entry_s)
    registry.insert(0, entry_n)
    
    # Write back
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"Added 2 new entries to {registry_path}")
    print(f"YOLOv8n: mAP50={entry_n['mAP50']}, mAP50-95={entry_n['mAP50_95']}")
    print(f"YOLOv8s: mAP50={entry_s['mAP50']}, mAP50-95={entry_s['mAP50_95']}")

if __name__ == '__main__':
    main()