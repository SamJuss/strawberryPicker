#!/usr/bin/env python3
"""
Check which models from training_history.csv are missing their directories/files
"""

import csv
import os
from pathlib import Path


def main():
    """Check for missing model directories."""

    # Read CSV and extract run IDs
    csv_runs = set()
    with open('model/training_history.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            run_id = row['run_id'].strip()
            if run_id and (run_id.startswith('run_') or run_id.startswith('kaggle_')):
                csv_runs.add(run_id)

    print(f"Found {len(csv_runs)} runs in CSV")

    # Find existing directories
    existing_dirs = set()
    for root, dirs, files in os.walk('model'):
        for dir_name in dirs:
            if dir_name.startswith('run_') or dir_name.startswith('kaggle_'):
                existing_dirs.add(dir_name)

    print(f"Found {len(existing_dirs)} model directories")

    # Find missing ones
    missing = csv_runs - existing_dirs
    extra = existing_dirs - csv_runs

    print(f"\nMissing model directories ({len(missing)}):")
    for run_id in sorted(missing):
        print(f"  - {run_id}")

    print(f"\nExtra directories not in CSV ({len(extra)}):")
    for dir_name in sorted(extra):
        print(f"  - {dir_name}")

    # Check for model files in existing directories
    print("\nModel files check:")
    for run_id in sorted(csv_runs):
        # Look for directories containing this run_id
        model_found = False
        for root, dirs, files in os.walk('model'):
            for dir_name in dirs:
                if run_id in dir_name:
                    dir_path = Path(root) / dir_name
                    weights_dir = dir_path / 'weights'
                    if weights_dir.exists():
                        best_pt = weights_dir / 'best.pt'
                        last_pt = weights_dir / 'last.pt'
                        if best_pt.exists() or last_pt.exists():
                            model_found = True
                            break
                    # Also check for .pt files directly in the directory
                    for file in dir_path.glob('*.pt'):
                        model_found = True
                        break
            if model_found:
                break

        status = "✓ Model found" if model_found else "✗ No model file"
        print(f"  {run_id}: {status}")


if __name__ == '__main__':
    main()