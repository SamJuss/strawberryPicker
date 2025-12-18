# Machine Learning Guide for Strawberry Picker

This comprehensive guide covers the machine learning pipeline, training methodologies, model architectures, and deployment strategies used in the Strawberry Picker project.

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Machine Learning Pipeline](#machine-learning-pipeline)
3. [Model Architectures](#model-architectures)
4. [Training Methodologies](#training-methodologies)
5. [Data Management](#data-management)
6. [Model Evaluation](#model-evaluation)
7. [Deployment & Inference](#deployment--inference)
8. [Performance Optimization](#performance-optimization)
9. [Troubleshooting](#troubleshooting)

## 🎯 Project Overview

The Strawberry Picker uses a two-stage AI pipeline:

1. **Detection Stage**: YOLO models identify and locate strawberries in images
2. **Classification Stage**: CNN models determine ripeness of detected strawberries

### Key Performance Metrics
- **Detection mAP@0.5**: 0.85+ (YOLOv8s)
- **Classification Accuracy**: 91.71% (EfficientNet-B0)
- **Real-time Inference**: <100ms per frame
- **Edge Deployment**: Raspberry Pi compatible

## 🔄 Machine Learning Pipeline

### Data Collection & Preparation
```python
# Image capture pipeline
├── Camera calibration (OpenCV)
├── Multi-angle image capture
├── Lighting normalization
└── Dataset curation
```

### Training Pipeline
```python
# Automated training workflow
├── Data preprocessing & augmentation
├── Model training with early stopping
├── Validation & hyperparameter tuning
├── Model export (ONNX, TFLite)
└── Performance benchmarking
```

### Inference Pipeline
```python
# Real-time processing
├── Image preprocessing
├── Object detection (YOLO)
├── Crop extraction
├── Ripeness classification
└── Decision making
```

## 🏗️ Model Architectures

### Detection Models

#### YOLOv8s (Primary Detection Model)
```yaml
Architecture: YOLOv8s
Input Size: 640x640
Backbone: CSPDarknet53
Neck: PANet
Head: Decoupled Head
Parameters: 11.2M
GFLOPs: 28.6
```

**Training Configuration:**
```python
model = YOLO('yolov8s.pt')
results = model.train(
    data='data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    patience=20,
    save=True,
    project='detection',
    name='yolov8s_enhanced'
)
```

#### YOLOv11n (Alternative Model)
```yaml
Architecture: YOLOv11n
Input Size: 640x640
Backbone: C2f-ELAN
Neck: C2f-PAN
Head: Decoupled Head
Parameters: 2.6M
GFLOPs: 6.5
```

### Classification Models

#### EfficientNet-B0 (Primary Classifier)
```python
import torch
from torchvision import models

# Model architecture
model = models.efficientnet_b0(pretrained=True)
model.classifier = torch.nn.Sequential(
    torch.nn.Dropout(p=0.2),
    torch.nn.Linear(1280, 4)  # 4 ripeness classes
)

# Training configuration
optimizer = torch.optim.AdamW(model.parameters(), lr=0.002)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50)
criterion = torch.nn.CrossEntropyLoss()
```

**Model Specifications:**
- Input: 128x128 RGB images
- Output: 4-class probabilities
- Parameters: ~4.7M
- Accuracy: 91.71%

## 🎯 Training Methodologies

### Data Augmentation Strategy
```python
from torchvision import transforms

train_transforms = transforms.Compose([
    transforms.RandomResizedCrop(128, scale=(0.8, 1.0)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.2),
    transforms.RandomRotation(degrees=15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
```

### Training Best Practices

#### Detection Training
```python
# YOLO training parameters
training_config = {
    'epochs': 100,
    'batch_size': 16,
    'img_size': 640,
    'patience': 20,
    'optimizer': 'AdamW',
    'lr0': 0.002,
    'lrf': 0.01,
    'momentum': 0.937,
    'weight_decay': 0.0005,
    'warmup_epochs': 3,
    'warmup_momentum': 0.8,
    'warmup_bias_lr': 0.1
}
```

#### Classification Training
```python
# EfficientNet training parameters
training_config = {
    'epochs': 50,
    'batch_size': 8,
    'learning_rate': 0.002,
    'weight_decay': 1e-4,
    'scheduler': 'cosine',
    'T_max': 50,
    'eta_min': 1e-6,
    'label_smoothing': 0.1,
    'mixup_alpha': 0.2
}
```

### Hyperparameter Optimization
```python
# Grid search for optimal parameters
param_grid = {
    'lr': [0.001, 0.002, 0.005],
    'batch_size': [8, 16, 32],
    'weight_decay': [1e-4, 1e-5],
    'scheduler': ['cosine', 'step']
}
```

## 📊 Data Management

### Dataset Structure
```
datasets/
├── strawberry_detect_v3/
│   ├── train/
│   │   ├── images/
│   │   └── labels/
│   ├── valid/
│   │   ├── images/
│   │   └── labels/
│   └── test/
│       ├── images/
│       └── labels/
├── ripeness_classification/
│   ├── ripe/
│   ├── unripe/
│   ├── partially_ripe/
│   └── overripe/
└── data.yaml
```

### Data Quality Assurance
```python
# Dataset validation
def validate_dataset(data_path):
    """Validate dataset integrity and annotations"""
    issues = []

    # Check image-label correspondence
    for split in ['train', 'valid', 'test']:
        img_dir = Path(data_path) / split / 'images'
        lbl_dir = Path(data_path) / split / 'labels'

        for img_path in img_dir.glob('*.jpg'):
            lbl_path = lbl_dir / f"{img_path.stem}.txt"
            if not lbl_path.exists():
                issues.append(f"Missing label for {img_path}")

    return issues
```

### Data Versioning
```yaml
# data.yaml configuration
path: ../datasets/strawberry_detect_v3
train: train
valid: valid
test: test

names:
  0: strawberry

# Metadata
version: 3.0
description: Strawberry detection dataset v3
created: 2025-12-17
size: 2500 images
classes: 1
```

## 📈 Model Evaluation

### Detection Metrics
```python
# YOLO evaluation metrics
def evaluate_detection_model(model_path, data_path):
    """Comprehensive detection evaluation"""
    model = YOLO(model_path)

    # Run validation
    results = model.val(data=data_path, split='test')

    metrics = {
        'mAP50': results.box.map50,
        'mAP50-95': results.box.map,
        'precision': results.box.mp,
        'recall': results.box.mr,
        'f1_score': 2 * (results.box.mp * results.box.mr) / (results.box.mp + results.box.mr)
    }

    return metrics
```

### Classification Metrics
```python
# Classification evaluation
def evaluate_classification_model(model, test_loader):
    """Detailed classification evaluation"""
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # Calculate metrics
    accuracy = accuracy_score(all_labels, all_preds)
    precision = precision_score(all_labels, all_preds, average='weighted')
    recall = recall_score(all_labels, all_preds, average='weighted')
    f1 = f1_score(all_labels, all_preds, average='weighted')

    # Confusion matrix
    cm = confusion_matrix(all_labels, all_preds)

    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'confusion_matrix': cm
    }
```

### Performance Benchmarks
```python
# Inference speed testing
def benchmark_inference(model, input_size=(640, 640), num_runs=100):
    """Benchmark model inference speed"""
    model.eval()
    times = []

    with torch.no_grad():
        for _ in range(num_runs):
            dummy_input = torch.randn(1, 3, *input_size)

            start_time = time.time()
            _ = model(dummy_input)
            end_time = time.time()

            times.append(end_time - start_time)

    avg_time = np.mean(times)
    fps = 1.0 / avg_time

    return {
        'avg_inference_time': avg_time * 1000,  # ms
        'fps': fps,
        'std_time': np.std(times) * 1000
    }
```

## 🚀 Deployment & Inference

### ONNX Export
```python
# Export YOLO model to ONNX
def export_to_onnx(model_path, output_path, input_size=(640, 640)):
    """Export PyTorch model to ONNX format"""
    model = YOLO(model_path)

    # Export with dynamic batch size
    model.export(
        format='onnx',
        imgsz=input_size,
        dynamic=True,
        simplify=True
    )
```

### TFLite Export for Edge Devices
```python
# Export classification model to TFLite
def export_to_tflite(model, output_path):
    """Export PyTorch model to TensorFlow Lite"""
    # Convert to TorchScript first
    scripted_model = torch.jit.script(model)
    scripted_model.save('temp_model.pt')

    # Use onnx2tf or similar tools for conversion
    # This requires additional setup
    pass
```

### Optimized Inference Pipeline
```python
class OptimizedInferencePipeline:
    """Optimized inference pipeline for real-time processing"""

    def __init__(self, detection_model_path, classification_model_path):
        # Load optimized models
        self.detector = YOLO(detection_model_path)
        self.classifier = self._load_classifier(classification_model_path)

        # Preprocessing pipelines
        self.detector_preprocess = self._get_detector_preprocess()
        self.classifier_preprocess = self._get_classifier_preprocess()

    def process_frame(self, frame):
        """Process single frame with optimizations"""
        # Detection
        detections = self.detector(frame, conf=0.25, iou=0.45)

        results = []
        for detection in detections[0].boxes:
            # Extract crop
            x1, y1, x2, y2 = detection.xyxy[0].cpu().numpy()
            crop = frame[int(y1):int(y2), int(x1):int(x2)]

            # Classify ripeness
            ripeness = self._classify_crop(crop)

            results.append({
                'bbox': [x1, y1, x2, y2],
                'confidence': detection.conf.item(),
                'ripeness': ripeness
            })

        return results
```

## ⚡ Performance Optimization

### Model Quantization
```python
# Dynamic quantization for faster inference
def quantize_model(model):
    """Apply dynamic quantization to PyTorch model"""
    quantized_model = torch.quantization.quantize_dynamic(
        model,
        {torch.nn.Linear},  # Quantize linear layers
        dtype=torch.qint8
    )
    return quantized_model
```

### TensorRT Optimization
```python
# Convert ONNX to TensorRT for GPU acceleration
def convert_to_tensorrt(onnx_path, output_path):
    """Convert ONNX model to TensorRT engine"""
    import tensorrt as trt

    # Build TensorRT engine
    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)

    # Create network
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    parser = trt.OnnxParser(network, logger)

    # Parse ONNX
    with open(onnx_path, 'rb') as model:
        parser.parse(model.read())

    # Build engine
    config = builder.create_builder_config()
    config.max_workspace_size = 1 << 30  # 1GB
    config.set_flag(trt.BuilderFlag.FP16)  # Use FP16 precision

    engine = builder.build_engine(network, config)

    # Save engine
    with open(output_path, 'wb') as f:
        f.write(engine.serialize())

    return engine
```

### Memory Optimization
```python
# Memory-efficient inference
@torch.no_grad()
def memory_efficient_inference(model, inputs, batch_size=4):
    """Process large inputs in batches to save memory"""
    model.eval()
    results = []

    for i in range(0, len(inputs), batch_size):
        batch = inputs[i:i+batch_size]
        batch_results = model(batch)
        results.extend(batch_results)

        # Clear cache periodically
        if i % (batch_size * 10) == 0:
            torch.cuda.empty_cache()

    return results
```

## 🔧 Troubleshooting

### Common Training Issues

#### Overfitting Solutions
```python
# Regularization techniques
def add_regularization(model):
    """Add regularization to prevent overfitting"""
    # Dropout
    model.add_module('dropout', torch.nn.Dropout(0.5))

    # Weight decay in optimizer
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=0.001,
        weight_decay=1e-4  # L2 regularization
    )

    # Early stopping
    early_stopping = EarlyStopping(patience=10, min_delta=0.001)

    return model, optimizer, early_stopping
```

#### Data Imbalance Solutions
```python
# Handle class imbalance
def balance_dataset(dataset, strategy='oversample'):
    """Balance dataset classes"""
    if strategy == 'oversample':
        # Oversample minority classes
        sampler = WeightedRandomSampler(
            weights=class_weights,
            num_samples=len(dataset),
            replacement=True
        )
    elif strategy == 'undersample':
        # Undersample majority classes
        sampler = WeightedRandomSampler(
            weights=inverse_class_weights,
            num_samples=min_class_count * len(classes),
            replacement=False
        )

    return sampler
```

### Inference Issues

#### Memory Problems
```python
# Handle out-of-memory errors
def safe_inference(model, inputs, max_batch_size=1):
    """Safe inference with automatic batch size reduction"""
    try:
        return model(inputs)
    except RuntimeError as e:
        if "out of memory" in str(e):
            # Reduce batch size and retry
            if inputs.shape[0] > max_batch_size:
                half_batch = inputs.shape[0] // 2
                results1 = safe_inference(model, inputs[:half_batch])
                results2 = safe_inference(model, inputs[half_batch:])
                return torch.cat([results1, results2], dim=0)
            else:
                raise e
        else:
            raise e
```

#### Performance Bottlenecks
```python
# Profile inference performance
def profile_inference(model, sample_input):
    """Profile model inference to identify bottlenecks"""
    with torch.profiler.profile(
        activities=[torch.profiler.ProfilerActivity.CPU, torch.profiler.ProfilerActivity.CUDA],
        record_shapes=True
    ) as prof:

        with torch.no_grad():
            _ = model(sample_input)

    # Print profiling results
    print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=10))

    return prof
```

## 📚 Additional Resources

### Recommended Reading
- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [EfficientNet Paper](https://arxiv.org/abs/1905.11946)
- [PyTorch Best Practices](https://pytorch.org/tutorials/)
- [ONNX Model Optimization](https://onnx.ai/onnx/intro/)

### Tools & Libraries
- **Training**: PyTorch, Ultralytics YOLO
- **Data**: Albumentations, OpenCV
- **Visualization**: Matplotlib, Weights & Biases
- **Deployment**: ONNX, TensorRT, OpenVINO

### Community Resources
- [PyTorch Forums](https://discuss.pytorch.org/)
- [Ultralytics GitHub](https://github.com/ultralytics/ultralytics)
- [Computer Vision Discord](https://discord.gg/cv)

---

**Last Updated**: December 17, 2025
**Version**: 1.0
**Authors**: Strawberry Picker Team