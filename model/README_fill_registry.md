# Filling Missing Values in Training Registry

## Overview
The `training_registry.json` file contained many missing values (zeros, nulls) for metrics, hyperparameters, and metadata. This document describes the process used to fill these values from per-run artifacts.

## Missing Fields Identified
- **Metrics**: `val_precision`, `val_recall`, `val_map50`, `val_map50_95`, `train_loss`, `val_loss`
- **Hyperparameters**: `batch_size`, `image_size`, `learning_rate`, `optimizer`, `weight_decay`
- **Metadata**: `gpu_memory_peak_gb`, `training_time_minutes`, `config_path`, `model_path`
- **System Info**: `gpu_name`, `cpu_count`, `ram_total_gb`, `python_version`, etc.

## Source Artifacts
Each training run has artifacts that contain the missing data:

1. **`args.yaml`** - Training configuration with hyperparameters
2. **`results.csv`** - Epoch-by-epoch metrics and losses
3. **`README.md`** - Summary with performance metrics
4. **Directory structure** - Paths to models and configs

## Fill Process

### Script: `fill_registry.py`
The script iterates through each run in `training_registry.json` and:

1. **Finds the run directory** in `model/detection/` by matching run_id
2. **Extracts from args.yaml**:
   - Batch size, image size, epochs, learning rate, optimizer, weight decay
   - System information (GPU, CPU, RAM, versions)
3. **Extracts from results.csv**:
   - Final epoch metrics (precision, recall, mAP@50, mAP@50-95)
   - Training losses (box, cls, dfl)
   - Completed epochs
4. **Extracts from README.md**:
   - Performance summaries and mAP values
5. **Sets paths**:
   - `config_path` → `args.yaml`
   - `model_path` → `weights/best.pt`
   - `results_path` → run directory

### Validation
After filling, run:
```bash
python model/view_registry.py
```
This displays the registry with filled values and confirms no regressions.

### Export
To export the filled registry:
```bash
python -c "from model.validation.training_registry import get_registry; get_registry().export_to_csv()"
```

## Future Automation
To automatically fill future runs, integrate `fill_registry.py` into the training pipeline:

1. After training completes, run the fill script
2. Add to training scripts: `python model/fill_registry.py`
3. The script safely skips runs that already have complete data

## Notes
- Values are extracted from authoritative sources (training artifacts)
- Missing artifacts result in warnings but don't break the process
- System info uses reasonable defaults when not available
- The process is idempotent (can be run multiple times safely)