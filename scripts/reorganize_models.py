#!/usr/bin/env python3
"""
Script to reorganize model files according to training registry.
Moves model files from scattered locations into appropriate run folders.
Updates training_registry.json with new paths.
"""

import json
import os
import shutil
from pathlib import Path

# Base directories
BASE_DIR = Path.cwd()
MODEL_RESULTS_DIR = BASE_DIR / "model/results"
TRAINING_REGISTRY_PATH = BASE_DIR / "model/training_registry.json"

# Mapping from run_id to target folder (already created)
RUN_ID_TO_FOLDER = {
    "run_20251125_150400_manual_baseline": "run_20251125_150400_manual_baseline",
    "run_20251202_210737_yolov8s_enhanced": "run_20251202_210737_yolov8s_enhanced",
    "run_20251202_210739_yolov8n": "run_20251202_210739_yolov8n",
    "run_20251202_210740_baseline": "run_20251202_210740_baseline",
    "run_20251202_210741_yolov8s_improved_detection_v2_20251202_153433": "run_20251202_210741_yolov8s_improved_detection_v2_20251202_153433",
    "kaggle_strawberry_yolov8n_20251204_115538": "kaggle_strawberry_yolov8n_20251204_115538",
    "kaggle_strawberry_yolov8s_20251204_2105262": "kaggle_strawberry_yolov8s_20251204_2105262",
    "optimized_yolov8n_20251204_154529": "optimized_yolov8n_20251204_154529",
}

# Mapping from old paths to new run folders (based on registry entries)
# We'll derive from the registry entries
def load_registry():
    with open(TRAINING_REGISTRY_PATH, 'r') as f:
        return json.load(f)

def find_model_files():
    """Find all model files in the project."""
    model_extensions = ('.pt', '.pth', '.onnx', '.h5', '.keras')
    model_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        # Skip hidden directories and backup
        if any(part.startswith('.') for part in root.split(os.sep)):
            continue
        if 'model_backup' in root:
            continue
        for file in files:
            if file.endswith(model_extensions):
                full_path = Path(root) / file
                model_files.append(full_path)
    return model_files

def match_model_to_run(model_path, registry):
    """Determine which run_id a model file belongs to based on path patterns."""
    path_str = str(model_path)
    # Check for known patterns
    if 'strawberry_yolov8n.pt' in path_str:
        return 'run_20251125_150400_manual_baseline'
    elif 'strawberry_yolov8s_enhanced.pt' in path_str:
        return 'run_20251202_210737_yolov8s_enhanced'
    elif 'First_run_Baseline.pt' in path_str:
        return 'run_20251202_210740_baseline'
    elif 'yolov8s_improved_detection_v2_20251202_153433' in path_str:
        return 'run_20251202_210741_yolov8s_improved_detection_v2_20251202_153433'
    elif 'kaggle_strawberry_yolov8n' in path_str:
        return 'kaggle_strawberry_yolov8n_20251204_115538'
    elif 'kaggle_strawberry_yolov8s' in path_str:
        return 'kaggle_strawberry_yolov8s_20251204_2105262'
    elif 'optimized_yolov8n' in path_str:
        return 'optimized_yolov8n_20251204_154529'
    # If inside a run folder already, extract run_id from folder name
    for run_id, folder in RUN_ID_TO_FOLDER.items():
        if folder in path_str:
            return run_id
    return None

def move_model_file(model_path, run_id):
    """Move model file to the appropriate run folder."""
    if run_id not in RUN_ID_TO_FOLDER:
        print(f"Warning: No folder mapping for run_id {run_id}. Skipping.")
        return None
    target_dir = MODEL_RESULTS_DIR / RUN_ID_TO_FOLDER[run_id]
    target_dir.mkdir(parents=True, exist_ok=True)
    # Create a weights subdirectory if not exists
    weights_dir = target_dir / "weights"
    weights_dir.mkdir(exist_ok=True)
    target_path = weights_dir / model_path.name
    # If target exists, maybe rename with suffix
    if target_path.exists():
        # Add a suffix to avoid overwriting
        stem = model_path.stem
        suffix = 1
        while target_path.exists():
            new_name = f"{stem}_{suffix}{model_path.suffix}"
            target_path = weights_dir / new_name
            suffix += 1
    print(f"Moving {model_path} -> {target_path}")
    shutil.move(str(model_path), str(target_path))
    return target_path

def update_registry_paths(registry, moved_files):
    """Update model_path and results_path in registry."""
    for entry in registry:
        run_id = entry.get('run_id')
        if not run_id:
            continue
        if run_id in RUN_ID_TO_FOLDER:
            folder = RUN_ID_TO_FOLDER[run_id]
            # Update results_path
            entry['results_path'] = f"model/results/{folder}"
            # Update model_path if we have a moved file for this run
            # We'll set to the first .pt file in the weights subdirectory
            weights_dir = MODEL_RESULTS_DIR / folder / "weights"
            if weights_dir.exists():
                pt_files = list(weights_dir.glob("*.pt"))
                if pt_files:
                    entry['model_path'] = str(pt_files[0].relative_to(BASE_DIR))
                else:
                    # Keep original or set to None
                    pass
    return registry

def main():
    print("Loading registry...")
    registry = load_registry()
    
    print("Finding model files...")
    model_files = find_model_files()
    print(f"Found {len(model_files)} model files.")
    
    moved = []
    for mf in model_files:
        run_id = match_model_to_run(mf, registry)
        if run_id:
            new_path = move_model_file(mf, run_id)
            if new_path:
                moved.append((mf, new_path, run_id))
        else:
            print(f"Could not determine run for {mf}. Skipping.")
    
    print(f"Moved {len(moved)} files.")
    
    # Update registry
    print("Updating registry...")
    updated_registry = update_registry_paths(registry, moved)
    
    # Backup original registry
    backup_path = TRAINING_REGISTRY_PATH.with_suffix('.json.backup')
    shutil.copy(TRAINING_REGISTRY_PATH, backup_path)
    print(f"Backed up registry to {backup_path}")
    
    # Write updated registry
    with open(TRAINING_REGISTRY_PATH, 'w') as f:
        json.dump(updated_registry, f, indent=2)
    print("Updated registry saved.")
    
    # Create a summary file
    summary_path = BASE_DIR / "model_reorganization_summary.txt"
    with open(summary_path, 'w') as f:
        f.write("Model Reorganization Summary\n")
        f.write("============================\n\n")
        f.write(f"Total model files found: {len(model_files)}\n")
        f.write(f"Files moved: {len(moved)}\n\n")
        for old, new, run in moved:
            f.write(f"{run}: {old.name}\n")
            f.write(f"  from: {old}\n")
            f.write(f"  to:   {new}\n\n")
        f.write("\nUpdated registry entries:\n")
        for entry in updated_registry:
            f.write(f"{entry.get('run_id')}: model_path = {entry.get('model_path')}, results_path = {entry.get('results_path')}\n")
    print(f"Summary written to {summary_path}")

if __name__ == "__main__":
    main()