#!/usr/bin/env python3
"""
Generate Confusion Matrices for Training Runs

This script generates confusion matrices for training runs by running inference
on validation datasets and comparing predictions with ground truth labels.
"""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from ultralytics import YOLO
import pandas as pd
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import yaml


def load_yaml_config(config_path: Path) -> dict:
    """Load YAML configuration file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Could not load config {config_path}: {e}")
        return {}


def find_validation_data(run_dir: Path) -> tuple:
    """Find validation images and labels for a run."""
    # Look for validation data in various possible locations
    possible_paths = [
        run_dir / "validation",
        Path("model/dataset") / run_dir.name / "valid",
        Path("model/dataset_strawberry_kaggle") / "valid",
        Path("model/dataset_stem_label") / "valid"
    ]

    for val_path in possible_paths:
        if val_path.exists():
            images_dir = val_path / "images"
            labels_dir = val_path / "labels"
            if images_dir.exists() and labels_dir.exists():
                return images_dir, labels_dir

    return None, None


def get_ground_truth_labels(labels_dir: Path, class_names: list) -> dict:
    """Extract ground truth labels from YOLO format label files."""
    gt_labels = {}

    if not labels_dir.exists():
        return gt_labels

    for label_file in labels_dir.glob("*.txt"):
        image_name = label_file.stem
        gt_labels[image_name] = []

        try:
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        class_id = int(parts[0])
                        if class_id < len(class_names):
                            gt_labels[image_name].append(class_names[class_id])
        except Exception as e:
            print(f"Warning: Could not read {label_file}: {e}")

    return gt_labels


def run_inference_and_generate_cm(model_path: Path, images_dir: Path, labels_dir: Path,
                                class_names: list, output_dir: Path, run_id: str):
    """Run inference and generate confusion matrix."""
    try:
        # Load model
        model = YOLO(str(model_path))

        # Get ground truth labels
        gt_labels = get_ground_truth_labels(labels_dir, class_names)

        if not gt_labels:
            print(f"No ground truth labels found for {run_id}")
            return False

        # Run inference
        results = model.predict(
            source=str(images_dir),
            conf=0.25,  # Confidence threshold
            iou=0.45,  # IoU threshold
            save=False,
            verbose=False
        )

        # Collect predictions and ground truth
        y_true = []
        y_pred = []

        for result in results:
            # Get image name
            img_path = Path(result.path)
            img_name = img_path.stem

            if img_name not in gt_labels:
                continue

            # Ground truth for this image
            gt_classes = gt_labels[img_name]

            # Predictions for this image
            pred_classes = []
            for box in result.boxes:
                class_id = int(box.cls.item())
                if class_id < len(class_names):
                    pred_classes.append(class_names[class_id])

            # For simplicity, we'll create a binary classification problem
            # Has strawberry vs no strawberry (for single class)
            # Or multi-class for multi-class problems
            if len(class_names) == 1:
                # Binary: strawberry present or not
                gt_has_strawberry = 1 if gt_classes else 0
                pred_has_strawberry = 1 if pred_classes else 0

                y_true.append(gt_has_strawberry)
                y_pred.append(pred_has_strawberry)
            else:
                # Multi-class: use all predictions (simplified)
                for gt_class in gt_classes:
                    y_true.append(gt_class)
                    # Find closest prediction or use background
                    if pred_classes:
                        y_pred.append(pred_classes[0])  # Simplified
                    else:
                        y_pred.append("background")

        if not y_true:
            print(f"No valid predictions/labels for {run_id}")
            return False

        # Generate confusion matrix
        if len(class_names) == 1:
            # Binary classification
            labels = [0, 1]  # 0 = no strawberry, 1 = strawberry
            display_labels = ["No Strawberry", "Strawberry"]
        else:
            # Multi-class
            all_classes = list(set(y_true + y_pred))
            labels = sorted(all_classes)
            display_labels = labels

        cm = confusion_matrix(y_true, y_pred, labels=labels)

        # Save confusion matrix as numpy array
        np.save(output_dir / f"confusion_matrix_{run_id}.npy", cm)

        # Generate and save plots
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=display_labels, yticklabels=display_labels)
        plt.title(f'Confusion Matrix - {run_id}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(output_dir / f"confusion_matrix_{run_id}.png", dpi=150, bbox_inches='tight')
        plt.close()

        # Normalized version
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        cm_normalized = np.nan_to_num(cm_normalized)  # Handle division by zero

        plt.figure(figsize=(10, 8))
        sns.heatmap(cm_normalized, annot=True, fmt='.2f', cmap='Blues',
                   xticklabels=display_labels, yticklabels=display_labels)
        plt.title(f'Normalized Confusion Matrix - {run_id}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(output_dir / f"confusion_matrix_normalized_{run_id}.png", dpi=150, bbox_inches='tight')
        plt.close()

        print(f"✓ Generated confusion matrix for {run_id}")
        return True

    except Exception as e:
        print(f"Error generating confusion matrix for {run_id}: {e}")
        return False


def main():
    """Main function to generate confusion matrices for all runs."""
    registry_path = Path('model/training_registry.json')

    # Load registry
    with open(registry_path, 'r') as f:
        registry = json.load(f)

    generated_count = 0

    for run in registry:
        run_id = run['run_id']
        model_path_str = run.get('model_path', '')

        if not model_path_str:
            continue

        model_path = Path(model_path_str)
        if not model_path.exists():
            continue

        # Find the run's directory
        run_dir = None
        detection_dir = Path('model/detection')
        for subdir in detection_dir.iterdir():
            if subdir.is_dir() and run_id in subdir.name:
                run_dir = subdir
                break

        if not run_dir:
            continue

        # Find validation data
        images_dir, labels_dir = find_validation_data(run_dir)

        if not images_dir or not labels_dir:
            print(f"No validation data found for {run_id}")
            continue

        # Get class names
        class_names = run.get('class_names', ['strawberry'])

        # Create output directory
        output_dir = run_dir
        output_dir.mkdir(exist_ok=True)

        # Generate confusion matrix
        success = run_inference_and_generate_cm(
            model_path, images_dir, labels_dir, class_names, output_dir, run_id
        )

        if success:
            generated_count += 1

    print(f"✓ Generated confusion matrices for {generated_count} runs")


if __name__ == '__main__':
    main()