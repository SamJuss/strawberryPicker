# Training Plan for Homemade Strawberry Dataset

## Dataset Overview
- **Location**: `model/dataset_homemade/`
- **Images**: 31 JPG files (WIN_20251219_*.jpg)
- **Status**: Unlabeled
- **Goal**: Train a YOLOv8 model for strawberry detection

---

## Phase 1: Labeling (Manual Step Required)

### Step 1.1: Install Labeling Tool
```bash
pip install labelImg
```

### Step 1.2: Launch LabelImg
```bash
labelImg model/dataset_homemade model/dataset_homemade/classes.txt
```

### Step 1.3: Label All Images
- Draw bounding boxes around each strawberry
- Save labels in YOLO format (will create .txt files)
- Verify each .jpg has a corresponding .txt file

**Expected Output**: 31 .txt label files in `model/dataset_homemade/`

---

## Phase 2: Dataset Preparation (Automated)

### Step 2.1: Copy to Labeled Dataset Structure
After labeling, run:
```bash
# Copy images and labels to structured dataset
cp model/dataset_homemade/*.jpg model/dataset_homemade_labeled/train/images/
cp model/dataset_homemade/*.txt model/dataset_homemade_labeled/train/labels/
```

### Step 2.2: Split Dataset
Since you have 31 images, I recommend:
- **Training**: 22 images (70%)
- **Validation**: 6 images (20%)
- **Test**: 3 images (10%)

Run this Python script to split:
```python
import os
import random
import shutil

src_img = 'model/dataset_homemade_labeled/train/images'
src_lbl = 'model/dataset_homemade_labeled/train/labels'
val_img = 'model/dataset_homemade_labeled/valid/images'
val_lbl = 'model/dataset_homemade_labeled/valid/labels'
test_img = 'model/dataset_homemade_labeled/test/images'
test_lbl = 'model/dataset_homemade_labeled/test/labels'

# Get all images
images = [f for f in os.listdir(src_img) if f.endswith('.jpg')]
random.shuffle(images)

# Split
val_images = images[:6]
test_images = images[6:9]
train_images = images[9:]

# Move files
for img in val_images:
    shutil.move(os.path.join(src_img, img), os.path.join(val_img, img))
    shutil.move(os.path.join(src_lbl, img.replace('.jpg', '.txt')), os.path.join(val_lbl, img.replace('.jpg', '.txt')))

for img in test_images:
    shutil.move(os.path.join(src_img, img), os.path.join(test_img, img))
    shutil.move(os.path.join(src_lbl, img.replace('.jpg', '.txt')), os.path.join(test_lbl, img.replace('.jpg', '.txt')))
```

### Step 2.3: Create data.yaml
Create `model/dataset_homemade_labeled/data.yaml`:
```yaml
path: /home/user/machine-learning/GitHubRepos/strawberryPicker/model/dataset_homemade_labeled
train: train/images
val: valid/images
test: test/images

nc: 1
names: ['strawberry']
```

---

## Phase 3: Model Training

### Step 3.1: Choose Model Architecture
For 31 images, I recommend **YOLOv8n** (nano) to avoid overfitting:
- Fast training
- Good for small datasets
- Less prone to overfitting

### Step 3.2: Training Configuration
```python
from ultralytics import YOLO

# Load model
model = YOLO('yolov8n.pt')

# Train
results = model.train(
    data='model/dataset_homemade_labeled/data.yaml',
    epochs=50,  # Start with 50 epochs
    imgsz=640,
    batch=8,
    name='homemade_yolov8n_50epochs',
    project='model/detection',
    patience=10,  # Early stopping
    save=True,
    save_period=10,
    cache=True
)
```

### Step 3.3: Training Script
Save as `scripts/train_homemade_dataset.py`:
```python
from ultralytics import YOLO
import os

def train_homemade_model():
    # Create output directory
    os.makedirs('model/detection/homemade_training', exist_ok=True)
    
    # Load pretrained model
    model = YOLO('yolov8n.pt')
    
    # Train
    results = model.train(
        data='model/dataset_homemade_labeled/data.yaml',
        epochs=50,
        imgsz=640,
        batch=8,
        name='homemade_yolov8n_50epochs',
        project='model/detection',
        patience=10,
        save=True,
        save_period=10,
        cache=True,
        device=0  # Use GPU if available
    )
    
    print(f"Training completed! Best model saved at:")
    print(f"model/detection/homemade_yolov8n_50epochs/weights/best.pt")
    
    return results

if __name__ == '__main__':
    train_homemade_model()
```

---

## Phase 4: Evaluation & Testing

### Step 4.1: Evaluate Model
```python
from ultralytics import YOLO

# Load trained model
model = YOLO('model/detection/homemade_yolov8n_50epochs/weights/best.pt')

# Evaluate on validation set
metrics = model.val(data='model/dataset_homemade_labeled/data.yaml')

print(f"mAP50: {metrics.box.map50}")
print(f"mAP50-95: {metrics.box.map}")
```

### Step 4.2: Test Inference
```python
from ultralytics import YOLO
import cv2

# Load model
model = YOLO('model/detection/homemade_yolov8n_50epochs/weights/best.pt')

# Test on sample image
results = model('model/dataset_homemade_labeled/test/images/WIN_20251219_*.jpg')

# Save results
for i, r in enumerate(results):
    r.save(f'test_result_{i}.jpg')
```

---

## Expected Timeline
- **Labeling**: 30-60 minutes (manual)
- **Dataset prep**: 5 minutes (automated)
- **Training**: 15-30 minutes (depending on GPU)
- **Evaluation**: 5 minutes

---

## Tips for Success
1. **Label carefully**: With only 31 images, quality is critical
2. **Consistent boxes**: Draw boxes the same way for all strawberries
3. **Include all strawberries**: Don't miss any visible strawberries
4. **Check labels**: Verify a few label files before training
5. **Monitor for overfitting**: With small datasets, overfitting is likely
6. **Consider data augmentation**: If performance is poor, we can add augmentations

---

## Next Steps After Training
1. Evaluate if model performance is satisfactory
2. If underfitting: Increase epochs or use larger model (YOLOv8s)
3. If overfitting: Add data augmentation or collect more images
4. Test on real robot scenario
5. Integrate with Arduino control system

---

## Questions to Consider
1. Do you want to label all 31 images, or should we start with a subset?
2. Are all strawberries ripe, or do you want to detect unripe ones too?
3. Should we create a multi-class dataset (e.g., ripe vs unripe)?
4. What's your target performance (mAP50)?

Let me know when you've completed the labeling, and I'll help you with the automated steps!