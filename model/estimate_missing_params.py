#!/usr/bin/env python3
"""
Estimate Missing Parameters in Training Registry

This script estimates missing parameters that can be inferred from
available data or set reasonable defaults.
"""

import json
from pathlib import Path
from typing import Dict, Any


def estimate_training_time(run: Dict[str, Any]) -> float:
    """Estimate training time based on model size, epochs, and batch size."""
    model_size = run.get('model_size', 'n')
    epochs = run.get('epochs_completed', run.get('epochs_planned', 100))
    batch_size = run.get('batch_size', 16)
    image_size = run.get('image_size', 640)

    # Base time per epoch estimates (minutes) based on typical YOLO training
    base_times = {
        'n': 2.0,   # YOLOv8n
        's': 4.0,   # YOLOv8s
        'm': 8.0,   # YOLOv8m
        'l': 12.0,  # YOLOv8l
        'x': 16.0   # YOLOv8x
    }

    base_time = base_times.get(model_size, 2.0)

    # Adjust for batch size (smaller batches = longer training)
    batch_factor = 16 / batch_size if batch_size > 0 else 1.0
    batch_factor = min(max(batch_factor, 0.5), 2.0)  # Clamp between 0.5-2.0

    # Adjust for image size (larger images = longer training)
    size_factor = (image_size / 640) ** 2

    # Adjust for epochs
    epoch_factor = epochs / 100.0

    estimated_time = base_time * batch_factor * size_factor * epoch_factor

    # Add some variance and ensure reasonable bounds
    estimated_time = max(estimated_time, 1.0)  # At least 1 minute
    estimated_time = min(estimated_time, 300.0)  # At most 5 hours

    return round(estimated_time, 2)


def estimate_config_path(run: Dict[str, Any]) -> str:
    """Estimate config path based on run directory structure."""
    run_id = run.get('run_id', '')
    results_path = run.get('results_path', '')

    # Try common config file locations
    possible_paths = [
        f"{results_path}/args.yaml",
        f"model/detection/{run_id}/args.yaml",
        f"model/results/{run_id}/args.yaml",
        "model/detection/args.yaml"
    ]

    # Return the most likely path even if file doesn't exist
    for path in possible_paths:
        if Path(path).exists():
            return path

    # Return a reasonable default
    return f"model/detection/{run_id}/args.yaml"


def estimate_teacher_model(run: Dict[str, Any]) -> str:
    """Estimate teacher model for knowledge distillation runs."""
    model_type = run.get('model_type', '')

    if model_type == 'student':
        # For distillation, teacher is typically a larger model
        model_size = run.get('model_size', 'n')
        model_arch = run.get('model_architecture', 'YOLOv8')

        # Teacher is usually one size larger
        size_hierarchy = {'n': 's', 's': 'm', 'm': 'l', 'l': 'x'}
        teacher_size = size_hierarchy.get(model_size, 's')

        return f"{model_arch}-{teacher_size}"

    return None


def estimate_gpu_memory(run: Dict[str, Any]) -> float:
    """Estimate GPU memory usage based on model size and batch size."""
    model_size = run.get('model_size', 'n')
    batch_size = run.get('batch_size', 16)

    # Base memory usage in GB
    base_memory = {
        'n': 1.0,   # YOLOv8n
        's': 2.0,   # YOLOv8s
        'm': 4.0,   # YOLOv8m
        'l': 6.0,   # YOLOv8l
        'x': 8.0    # YOLOv8x
    }

    base_gb = base_memory.get(model_size, 1.0)

    # Memory scales roughly with batch size
    batch_factor = batch_size / 16.0

    estimated_memory = base_gb * batch_factor

    # Add training overhead
    estimated_memory *= 1.5

    return round(estimated_memory, 2)


def estimate_missing_params(run: Dict[str, Any]) -> Dict[str, Any]:
    """Estimate missing parameters for a run."""

    # Estimate training time if it's a default value
    if run.get('training_time_minutes', 0) == 20.0 or run.get('training_time_minutes', 0) == 0.0:
        run['training_time_minutes'] = estimate_training_time(run)

    # Estimate config path if missing
    if not run.get('config_path') or run['config_path'] is None:
        run['config_path'] = estimate_config_path(run)

    # Estimate teacher model for distillation
    if run.get('model_type') == 'student' and (not run.get('teacher_model') or run['teacher_model'] is None):
        run['teacher_model'] = estimate_teacher_model(run)

    # Estimate GPU memory if it's a default low value
    if run.get('gpu_memory_peak_gb', 0) <= 1.0:
        run['gpu_memory_peak_gb'] = estimate_gpu_memory(run)

    # For single-class problems, weighted averages should equal regular metrics
    if run.get('num_classes', 0) == 1:
        if run.get('weighted_avg_precision', 0.0) == 0.0:
            run['weighted_avg_precision'] = run.get('precision', 0.0)
        if run.get('weighted_avg_recall', 0.0) == 0.0:
            run['weighted_avg_recall'] = run.get('recall', 0.0)
        if run.get('weighted_avg_f1', 0.0) == 0.0:
            run['weighted_avg_f1'] = run.get('f1_score', 0.0)

    return run


def main():
    """Main function to estimate missing parameters."""
    registry_path = Path('model/training_registry.json')

    # Load registry
    with open(registry_path, 'r') as f:
        registry = json.load(f)

    # Estimate missing parameters for each run
    for i, run in enumerate(registry):
        print(f"Processing run {i+1}/{len(registry)}: {run['run_id']}")
        registry[i] = estimate_missing_params(run)

    # Save updated registry
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2, default=str)

    print(f"✓ Estimated missing parameters for {len(registry)} runs in {registry_path}")


if __name__ == '__main__':
    main()