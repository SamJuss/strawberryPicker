# YOLOv8s Strawberry Stem Detection Model v2

## Overview
This model was trained on December 18, 2025, for detecting strawberry stems in images. It achieves excellent performance with 98.4% mAP@50 and is optimized for integration with the robotic picking system.

## Model Details
- **Architecture**: YOLOv8s
- **Classes**: 2 (stem, strawberry)
- **Input Size**: 640x640
- **Training Epochs**: 56 (early stopped)
- **Training Time**: 12.7 minutes

## Performance Metrics
- **mAP@50**: 0.984 (98.4%)
- **mAP@50-95**: 0.693 (69.3%)
- **Precision**: 0.971 (97.1%)
- **Recall**: 0.973 (97.3%)

## Files
- `weights/best.pt` - Best performing model checkpoint
- `weights/last.pt` - Final epoch model
- `weights/epoch*.pt` - Checkpoint models every 10 epochs
- `weights/strawberry_yolov8n.onnx` - ONNX export for deployment
- `args.yaml` - Training configuration
- `results.csv` - Training metrics per epoch
- `results.png` - Training curves and validation results
- `confusion_matrix*.png` - Confusion matrices
- `Box*.png` - Precision-Recall curves
- `train_batch*.jpg` - Training batch visualizations
- `val_batch*.jpg` - Validation batch predictions

## Usage

### Python Inference
```python
from ultralytics import YOLO

# Load model
model = YOLO('weights/best.pt')

# Run inference
results = model.predict('path/to/image.jpg', conf=0.5)
```

### ONNX Inference
```python
import onnxruntime as ort
import numpy as np

# Load ONNX model
session = ort.InferenceSession('weights/strawberry_yolov8n.onnx')

# Prepare input
input_data = preprocess_image(image)  # Your preprocessing
outputs = session.run(None, {'input': input_data})
```

## Training Configuration
- **Dataset**: `model/dataset_stem_label`
- **Batch Size**: 16
- **Image Size**: 640x640
- **Optimizer**: AdamW (auto-selected)
- **Learning Rate**: 0.001667 (initial)
- **Early Stopping**: Patience 20 epochs
- **Data Augmentation**: Enabled (rotation, flip, color jitter)

## Integration Notes
This model is designed for the strawberry picking pipeline and should be used with:
- Coordinate transformer for pixel-to-world conversion
- Arduino bridge for robotic arm control
- Ripeness classifier for fruit quality assessment

## Training Registry
Run ID: `run_20251218_133358_yolov8s_stem_detection`

---
**Created**: December 18, 2025
**Training Time**: 12.7 minutes
**GPU**: NVIDIA GeForce RTX 3050 Ti Laptop GPU