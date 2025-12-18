#!/usr/bin/env python3
"""
Merge Archived Registry with Current Registry

This script merges data from the archived training_registry.json with the current one,
preserving recent improvements while adding historical data.
"""

import json
from pathlib import Path
from typing import Dict, List, Any


def load_registry(file_path: Path) -> List[Dict[str, Any]]:
    """Load registry from JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Handle different structures
        if isinstance(data, dict) and 'models' in data:
            return data['models']
        elif isinstance(data, list):
            return data
        else:
            print(f"Unexpected registry structure in {file_path}")
            return []
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []


def merge_run_data(current_run: Dict[str, Any], archived_run: Dict[str, Any]) -> Dict[str, Any]:
    """Merge data from archived run into current run, preserving current improvements."""

    # Fields to preserve from current (our improvements)
    preserve_fields = {
        'confusion_matrix',  # Our generated confusion matrices
        'macro_avg_precision', 'macro_avg_recall', 'macro_avg_f1',
        'weighted_avg_precision', 'weighted_avg_recall', 'weighted_avg_f1',
        'f1_score', 'val_accuracy', 'mAP50', 'mAP50_95'
    }

    merged = current_run.copy()

    # For each field in archived run
    for key, value in archived_run.items():
        # Skip if we already have this field and it's in preserve list
        if key in merged and key in preserve_fields:
            continue

        # Skip null/empty values unless current is also null/empty
        if value is None or value == '' or value == []:
            if merged.get(key) not in [None, '', []]:
                continue

        # Skip if current has a better/non-zero value
        current_value = merged.get(key)
        if (isinstance(current_value, (int, float)) and current_value != 0 and
            isinstance(value, (int, float)) and value == 0):
            continue

        # Otherwise, use archived value
        merged[key] = value

    return merged


def main():
    """Main function to merge registries."""
    current_path = Path('model/training_registry.json')
    archived_path = Path('/home/user/machine-learning/GitHubRepos/strawberrypickertrainingregistry/training_registry.json')

    # Load both registries
    current_registry = load_registry(current_path)
    archived_registry = load_registry(archived_path)

    print(f"Current registry: {len(current_registry)} runs")
    print(f"Archived registry: {len(archived_registry)} runs")

    # Create lookup by run_id for current registry
    current_by_id = {run['run_id']: run for run in current_registry}

    merged_registry = []
    added_count = 0
    updated_count = 0

    # Process each archived run
    for archived_run in archived_registry:
        run_id = archived_run.get('run_id')
        if not run_id:
            continue

        if run_id in current_by_id:
            # Merge with existing
            merged_run = merge_run_data(current_by_id[run_id], archived_run)
            merged_registry.append(merged_run)
            updated_count += 1
        else:
            # Add new run
            merged_registry.append(archived_run)
            added_count += 1

    # Add any current runs not in archived (shouldn't happen but safety check)
    archived_ids = {run.get('run_id') for run in archived_registry}
    for run in current_registry:
        if run['run_id'] not in archived_ids:
            merged_registry.append(run)

    print(f"Added {added_count} new runs from archive")
    print(f"Updated {updated_count} existing runs")
    print(f"Total merged runs: {len(merged_registry)}")

    # Sort by date (most recent first)
    def get_sort_key(run):
        date_str = run.get('date', '1970-01-01')
        if isinstance(date_str, str) and len(date_str) >= 10:
            return date_str[:10]
        return '1970-01-01'

    merged_registry.sort(key=get_sort_key, reverse=True)

    # Save merged registry
    with open(current_path, 'w') as f:
        json.dump(merged_registry, f, indent=2, default=str)

    print(f"✓ Merged registry saved to {current_path}")


if __name__ == '__main__':
    main()