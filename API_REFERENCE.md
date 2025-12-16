# API Reference Guide

## Core Classes

### YOLOv8Detector

The main detection class for strawberry identification.

```python
from src.yolov8_detector import YOLOv8Detector

# Initialize detector
detector = YOLOv8Detector(
    model_path='path/to/model.pt',
    device='cuda'  # or 'cpu'
)

# Detect strawberries in image
detections = detector.detect(image, conf_threshold=0.5)

# Batch processing
detections_batch = detector.detect_batch(images)
```

#### Methods

##### `detect(image, conf_threshold=0.5)`
Detect strawberries in a single image.

**Parameters:**
- `image` (np.ndarray): Input image
- `conf_threshold` (float): Confidence threshold (0.0-1.0)

**Returns:**
- `List[Detection]`: List of Detection objects

**Example:**
```python
import cv2
image = cv2.imread('strawberry.jpg')
detections = detector.detect(image, conf_threshold=0.7)

for detection in detections:
    print(f"Confidence: {detection.confidence:.2f}")
    print(f"Bounding box: {detection.xyxy}")
```

##### `detect_batch(images, conf_threshold=0.5)`
Detect strawberries in multiple images.

**Parameters:**
- `images` (List[np.ndarray]): List of input images
- `conf_threshold` (float): Confidence threshold

**Returns:**
- `List[List[Detection]]`: List of detection lists

### RipenessClassifier

Classifies strawberry ripeness levels.

```python
from src.ripeness_classifier import RipenessClassifier

classifier = RipenessClassifier('path/to/classifier.pt')

# Classify single image
ripeness = classifier.classify(strawberry_image)

# Batch classification
ripeness_batch = classifier.classify_batch(images)
```

#### Methods

##### `classify(image)`
Classify ripeness of a single strawberry image.

**Parameters:**
- `image` (np.ndarray): Cropped strawberry image

**Returns:**
- `RipenessResult`: Classification result with class and confidence

**Ripeness Classes:**
- `0`: Unripe (green)
- `1`: Ripe (red)
- `2`: Overripe (dark red/brown)

**Example:**
```python
ripeness = classifier.classify(cropped_strawberry)
print(f"Ripeness: {ripeness.class_name} ({ripeness.confidence:.2%})")
```

### ArduinoBridge

Controls the robotic arm via Arduino.

```python
from src.arduino_bridge import ArduinoBridge

arduino = ArduinoBridge(
    port='/dev/ttyUSB0',
    baudrate=115200
)

# Test connection
arduino.test_connection()

# Move to position
arduino.move_to_position(x=10.0, y=5.0, z=15.0, speed=1.0)

# Execute actions
arduino.cut_strawberry(duration=2.0)
arduino.emergency_stop()
```

#### Methods

##### `move_to_position(x, y, z, speed=1.0)`
Move robotic arm to 3D position.

**Parameters:**
- `x` (float): X coordinate in cm
- `y` (float): Y coordinate in cm  
- `z` (float): Z coordinate in cm
- `speed` (float): Movement speed (0.1-2.0)

##### `cut_strawberry(duration=2.0)`
Execute cutting action.

**Parameters:**
- `duration` (float): Cutting action duration in seconds

##### `emergency_stop()`
Immediately stop all movement.

### CoordinateTransformer

Transforms pixel coordinates to world coordinates.

```python
from src.coordinate_transformer import PixelToWorldTransformer

transformer = PixelToWorldTransformer(
    camera_matrix=camera_matrix,
    distortion_coeffs=distortion_coeffs,
    robot_base_position=[0, 0, 0],
    camera_height=50.0,
    camera_angle=45.0
)

# Transform coordinates
world_coords = transformer.pixel_to_world([320, 240])
```

#### Methods

##### `pixel_to_world(pixel_coords)`
Convert pixel coordinates to world coordinates.

**Parameters:**
- `pixel_coords` (Tuple[int, int]): (x, y) pixel coordinates

**Returns:**
- `Tuple[float, float, float]`: (x, y, z) world coordinates in cm

### StrawberryPickerPipeline

Complete end-to-end harvesting pipeline.

```python
from src.strawberry_picker_pipeline import StrawberryPickerPipeline

pipeline = StrawberryPickerPipeline(
    model_path='path/to/detection_model.pt',
    classifier_path='path/to/classification_model.pt',
    arduino_port='/dev/ttyUSB0',
    camera_index=0
)

# Start harvesting
pipeline.start_harvesting(
    target_count=50,
    confidence_threshold=0.7,
    max_runtime=300
)
```

#### Methods

##### `start_harvesting(target_count, confidence_threshold, max_runtime)`
Start the complete harvesting process.

**Parameters:**
- `target_count` (int): Number of strawberries to harvest
- `confidence_threshold` (float): Detection confidence threshold
- `max_runtime` (int): Maximum runtime in seconds

## Utility Functions

### Image Processing

```python
from src.utils import preprocess_image, draw_detections

# Preprocess image for model input
processed = preprocess_image(image, target_size=(640, 640))

# Draw detection results
annotated = draw_detections(image, detections)
```

### Data Loading

```python
from src.utils import load_dataset, save_dataset

# Load dataset
dataset = load_dataset('path/to/dataset')

# Save processed dataset
save_dataset(dataset, 'path/to/output')
```

## Configuration

### Model Configuration

```python
# config/model_config.yaml
detection:
  model_path: "huggingface_models/strawberry-yolov8s-detector/best.pt"
  confidence_threshold: 0.7
  input_size: [640, 640]
  device: "cuda"

classification:
  model_path: "models/ripeness_classifier.pt"
  classes: ["unripe", "ripe", "overripe"]
  input_size: [224, 224]

arduino:
  port: "/dev/ttyUSB0"
  baudrate: 115200
  timeout: 1.0

camera:
  index: 0
  resolution: [640, 480]
  fps: 30
```

### Loading Configuration

```python
import yaml
from src.config import Config

with open('config/model_config.yaml') as f:
    config = Config(yaml.safe_load(f))
```

## Error Handling

### Common Exceptions

```python
from src.exceptions import (
    ModelNotFoundError,
    CameraError,
    ArduinoConnectionError,
    DetectionError
)

try:
    detector = YOLOv8Detector('invalid/path.pt')
except ModelNotFoundError as e:
    print(f"Model file not found: {e}")

try:
    cap = cv2.VideoCapture(999)  # Invalid camera index
except CameraError as e:
    print(f"Camera error: {e}")
```

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use logger in classes
logger = logging.getLogger(__name__)
logger.info("Detection started")
```

## Performance Tips

### GPU Optimization

```python
# Use mixed precision
detector = YOLOv8Detector('model.pt', device='cuda')
detector.model.half()  # Convert to FP16

# Enable TensorRT if available
detector.model.export(format='engine')
```

### Memory Management

```python
# Clear GPU cache
import torch
torch.cuda.empty_cache()

# Use batch processing for efficiency
detections = detector.detect_batch(images, batch_size=8)
```

### Real-time Optimization

```python
# Use smaller input size for speed
detector = YOLOv8Detector('model.pt', input_size=(416, 416))

# Skip low-confidence detections
detections = [d for d in detections if d.confidence > 0.8]
```

## Examples

### Complete Detection Pipeline

```python
import cv2
from src.yolov8_detector import YOLOv8Detector
from src.coordinate_transformer import PixelToWorldTransformer

# Initialize components
detector = YOLOv8Detector('best.pt')
transformer = PixelToWorldTransformer(camera_matrix, distortion_coeffs)

# Capture and process
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detect strawberries
    detections = detector.detect(frame, conf_threshold=0.7)
    
    # Process each detection
    for detection in detections:
        # Get pixel coordinates
        pixel_x, pixel_y = detection.center
        
        # Transform to world coordinates
        world_x, world_y, world_z = transformer.pixel_to_world([pixel_x, pixel_y])
        
        print(f"Strawberry at world position: ({world_x:.1f}, {world_y:.1f}, {world_z:.1f})")
    
    # Display results
    annotated = detector.draw_detections(frame, detections)
    cv2.imshow('Detection', annotated)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Batch Processing

```python
import os
from src.yolov8_detector import YOLOv8Detector

detector = YOLOv8Detector('best.pt')

# Process all images in directory
image_dir = 'test_images'
results = []

for filename in os.listdir(image_dir):
    if filename.endswith(('.jpg', '.png', '.jpeg')):
        image_path = os.path.join(image_dir, filename)
        image = cv2.imread(image_path)
        
        detections = detector.detect(image)
        results.append({
            'filename': filename,
            'detections': len(detections),
            'confidences': [d.confidence for d in detections]
        })

# Print summary
for result in results:
    print(f"{result['filename']}: {result['detections']} strawberries detected")