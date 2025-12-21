# Training Tutorial

## Overview
Learn how to train your own strawberry detection models using the StrawberryPicker framework.

## Prerequisites
- GPU with 6GB+ VRAM
- 1000+ strawberry images
- Labeled dataset

## Step 1: Data Collection

### Using Webcam
```python
# Collect training images
python scripts/webcam_capture.py --output_dir data/raw_images --count 1000

# Capture images with different angles and lighting
# Ensure strawberries are clearly visible
```

### Using Existing Dataset
```python
# Import from other formats
python scripts/import_dataset.py --source /path/to/dataset --format yolo
```

## Step 2: Data Annotation

### Using Built-in Tool
```python
# Start web-based labeling interface
python model/labeling_web_interface.py

# Open browser to localhost:8080
# Draw bounding boxes around strawberries
# Save labels in YOLO format
```

### Manual Annotation
Use tools like:
- LabelImg
- CVAT
- Roboflow

Export format: YOLO with structure:
```
dataset/
  train/
    images/
    labels/
  valid/
    images/
    labels/
```

## Step 3: Dataset Configuration

Create `data.yaml`:
```yaml
train: ./dataset/train/images
val: ./dataset/valid/images
test: ./dataset/test/images

nc: 1  # number of classes
names: ['strawberry']  # class names
```

## Step 4: Training

### Basic Training
```python
from ultralytics import YOLO

# Load base model
model = YOLO('yolov8s.pt')  # or 'yolov8n.pt' for faster training

# Train
results = model.train(
    data='data.yaml',
    epochs=150,
    imgsz=640,
    batch=16,
    device=0,
    project='runs/detect',
    name='strawberry_experiment'
)
```

### Advanced Training
```python
# Custom training with optimization
results = model.train(
    data='data.yaml',
    epochs=200,
    imgsz=640,
    batch=32,
    device=0,
    project='runs/detect',
    name='strawberry_advanced',
    
    # Data augmentation
    hsv_h=0.015,
    hsv_s=0.7,
    hsv_v=0.4,
    degrees=10.0,
    translate=0.1,
    scale=0.5,
    shear=2.0,
    fliplr=0.5,
    mosaic=1.0,
    mixup=0.1,
    
    # Optimization
    lr0=0.01,
    lrf=0.01,
    momentum=0.937,
    weight_decay=0.0005,
    warmup_epochs=3.0,
    
    # Validation
    val=True,
    plots=True,
    save=True,
    save_json=True
)
```

## Step 5: Monitoring Training

### TensorBoard
```bash
tensorboard --logdir runs/detect/strawberry_experiment
```

### Weights & Biases
```python
# Add to training script
wandb.init(project="strawberry-detection")
```

## Step 6: Model Evaluation

```python
# Load trained model
model = YOLO('runs/detect/strawberry_experiment/weights/best.pt')

# Validate
results = model.val(
    data='data.yaml',
    imgsz=640,
    batch=32,
    device=0
)

print(f"mAP50-95: {results.box.map}")
print(f"Precision: {results.box.mp}")
print(f"Recall: {results.box.mr}")
```

## Step 7: Export Models

```python
# Export to ONNX
model.export(format='onnx', imgsz=640, dynamic=True)

# Export to TensorRT
model.export(format='engine', imgsz=640, device=0)

# Export to TFLite
model.export(format='tflite', imgsz=640)
```

## Step 8: Test Inference

```python
# Test with new images
results = model('test_images/strawberry_1.jpg')
results[0].show()

# Test with webcam
import cv2
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    results = model(frame)
    annotated = results[0].plot()
    cv2.imshow('Detection', annotated)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
```

## Tips for Better Results

1. **Data Quality**
   - Use high-resolution images (1080p+)
   - Ensure good lighting conditions
   - Include various strawberry sizes and orientations

2. **Data Augmentation**
   - Enable mosaic augmentation
   - Use color space augmentation
   - Apply random rotations and scales

3. **Training Parameters**
   - Start with smaller learning rate
   - Use warmup epochs
   - Monitor validation loss

4. **Hardware Optimization**
   - Use mixed precision training
   - Enable gradient checkpointing for large models
   - Use multiple GPUs if available

## Troubleshooting

### Common Issues
- **CUDA Out of Memory**: Reduce batch size
- **Poor Detection**: Check data quality and augmentation
- **Slow Training**: Enable mixed precision
- **Overfitting**: Reduce epochs or add more data

### Performance Optimization
```python
# Use mixed precision
model.train(mixed_precision=True)

# Enable gradient checkpointing
model.train(gradient_checkpointing=True)

# Use multiple GPUs
model.train(device=[0, 1, 2, 3])
```

## Next Steps
- Integrate with robotic system
- Deploy to edge devices
- Fine-tune for specific environments