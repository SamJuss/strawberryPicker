# Labeling Guide for Homemade Strawberry Dataset

## Overview
This guide explains how to label your 31 homemade strawberry images for object detection training.

## Labeling Tool Recommendation
For this small dataset (31 images), I recommend using **LabelImg** - a simple, open-source graphical image annotation tool.

### Installing LabelImg
```bash
pip install labelImg
```

### Running LabelImg
```bash
labelImg model/dataset_homemade model/dataset_homemade/classes.txt
```

## Classes
Create a `classes.txt` file in `model/dataset_homemade/` with:
```
strawberry
```

## Labeling Instructions

### 1. Setup
- Open LabelImg
- Set the directory to `model/dataset_homemade`
- Set save format to YOLO (not PascalVOC)
- Load the `classes.txt` file

### 2. Drawing Bounding Boxes
- Click "Open Dir" and select `model/dataset_homemade`
- For each image:
  - Draw a tight bounding box around each strawberry
  - Make sure the box includes the entire strawberry with minimal background
  - Don't include leaves or stems unless they're part of the fruit cluster
  - Press 'w' to draw a box, or click the rectangle icon

### 3. Quality Guidelines
- **Box tightness**: Boxes should be as tight as possible around strawberries
- **Occlusion**: If a strawberry is partially occluded, still draw a box around the visible portion
- **Size**: Label strawberries of all sizes (small to large)
- **Confidence**: Only label strawberries you're confident about
- **Multiple objects**: Label ALL visible strawberries in each image

### 4. Saving
- Press 'Ctrl+s' to save after each image
- Labels will be saved as `.txt` files with the same name as the image
- The format will be: `class_id center_x center_y width height` (all normalized 0-1)

### 5. Verification
After labeling all images, verify:
- Each `.jpg` file has a corresponding `.txt` file
- No empty label files (unless image has no strawberries)
- Check a few label files to ensure format is correct

## Alternative: Manual Label File Creation

If you prefer to create label files manually, each line in the `.txt` file should be:
```
0 x_center y_center width height
```

Where:
- `0` is the class ID (strawberry)
- `x_center`, `y_center`, `width`, `height` are normalized coordinates (0-1)

### Example Calculation:
For a strawberry at pixel coordinates:
- Top-left: (100, 150)
- Bottom-right: (200, 250)
- Image size: 640x480

Normalized values:
- x_center = (100 + 200) / 2 / 640 = 0.234
- y_center = (150 + 250) / 2 / 480 = 0.417
- width = (200 - 100) / 640 = 0.156
- height = (250 - 150) / 480 = 0.208

Label file content:
```
0 0.234 0.417 0.156 0.208
```

## Next Steps After Labeling
1. Copy labeled images and labels to the structured dataset
2. Create `data.yaml` file
3. Split into train/val/test sets
4. Train the model

## Tips
- Take breaks while labeling to maintain accuracy
- If unsure about a strawberry, it's better to label it than skip it
- Consistent labeling is more important than perfect labeling
- Review your first few labels to ensure you're following the guidelines