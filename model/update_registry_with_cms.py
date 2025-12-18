#!/usr/bin/env python3
"""
Update Registry with Generated Confusion Matrices

This script loads the generated confusion matrices and updates the registry
with the confusion matrix data.
"""

import json
import numpy as np
from pathlib import Path


def load_confusion_matrix(cm_path: Path) -> list:
    """Load confusion matrix from numpy file and convert to list."""
    try:
        cm = np.load(cm_path)
        return cm.tolist()
    except Exception as e:
        print(f"Warning: Could not load confusion matrix {cm_path}: {e}")
        return None


def update_run_with_cm(run: dict, detection_dir: Path) -> dict:
    """Update a run with confusion matrix data if available."""
    run_id = run['run_id']

    # Find the run's directory
    run_dir = None
    for subdir in detection_dir.iterdir():
        if subdir.is_dir() and run_id in subdir.name:
            run_dir = subdir
            break

    if not run_dir:
        return run

    # Look for confusion matrix file
    cm_file = run_dir / f"confusion_matrix_{run_id}.npy"
    if cm_file.exists():
        cm_data = load_confusion_matrix(cm_file)
        if cm_data is not None:
            run['confusion_matrix'] = cm_data
            print(f"✓ Updated confusion matrix for {run_id}")

    return run


def main():
    """Main function to update registry with confusion matrices."""
    registry_path = Path('model/training_registry.json')
    detection_dir = Path('model/detection')

    # Load registry
    with open(registry_path, 'r') as f:
        registry = json.load(f)

    # Update runs with confusion matrices
    updated_count = 0
    for i, run in enumerate(registry):
        original_cm = run.get('confusion_matrix')
        registry[i] = update_run_with_cm(run, detection_dir)

        if registry[i].get('confusion_matrix') != original_cm:
            updated_count += 1

    # Save updated registry
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2, default=str)

    print(f"✓ Updated {updated_count} runs with confusion matrix data")


if __name__ == '__main__':
    main()