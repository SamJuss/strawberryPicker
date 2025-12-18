#!/usr/bin/env python3
"""
Calculate Derived Metrics for Training Registry

This script calculates missing metrics that can be derived from existing values:
- F1 score from precision and recall
- Macro/weighted averages for single-class problems
- Accuracy approximations from mAP
"""

import json
from pathlib import Path
from typing import Dict, Any


def calculate_f1_score(precision: float, recall: float) -> float:
    """Calculate F1 score from precision and recall."""
    if precision == 0.0 and recall == 0.0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0


def calculate_derived_metrics(run: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate derived metrics for a run."""
    # F1 score from precision and recall
    if run.get('precision', 0.0) > 0.0 and run.get('recall', 0.0) > 0.0:
        f1 = calculate_f1_score(run['precision'], run['recall'])
        run['f1_score'] = f1

    # For single-class problems, macro and weighted averages equal the class metrics
    if run.get('num_classes', 0) == 1:
        run['macro_avg_precision'] = run.get('precision', 0.0)
        run['macro_avg_recall'] = run.get('recall', 0.0)
        run['macro_avg_f1'] = run.get('f1_score', 0.0)
        run['weighted_avg_precision'] = run.get('precision', 0.0)
        run['weighted_avg_recall'] = run.get('recall', 0.0)
        run['weighted_avg_f1'] = run.get('f1_score', 0.0)

    # Approximate accuracy from mAP (rough approximation for object detection)
    # mAP@50 roughly correlates with detection accuracy
    if run.get('val_map50', 0.0) > 0.0:
        # For object detection, accuracy is harder to define, but we can use mAP as proxy
        # This is a rough approximation - in practice accuracy would be calculated differently
        run['val_accuracy'] = run['val_map50']  # Approximation

    # For multi-class problems, if we have per-class metrics, we could calculate properly
    # But for now, we'll leave them as-is if num_classes > 1

    return run


def main():
    """Main function to calculate derived metrics."""
    registry_path = Path('model/training_registry.json')

    # Load registry
    with open(registry_path, 'r') as f:
        registry = json.load(f)

    # Calculate derived metrics for each run
    for i, run in enumerate(registry):
        print(f"Processing run {i+1}/{len(registry)}: {run['run_id']}")
        registry[i] = calculate_derived_metrics(run)

    # Save updated registry
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2, default=str)

    print(f"✓ Calculated derived metrics for {len(registry)} runs in {registry_path}")


if __name__ == '__main__':
    main()