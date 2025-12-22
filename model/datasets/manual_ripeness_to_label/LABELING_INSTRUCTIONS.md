# Ripeness Dataset Labeling Instructions

## 🍓 What to Label
Label **strawberries only** - ignore other fruits or objects.

## 🎯 Goal
- Find ripe strawberries in unripe/overripe images
- All labeled strawberries are **ripe** (class 0)
- This adds manual ripeness detection to your model

## 📋 Categories
- **Unripe images**: Look for strawberries that look ripe/yellowish
- **Overripe images**: Look for strawberries that still look fresh/red

## ✅ Labeling Tips
1. Draw tight bounding boxes around strawberries
2. Only label strawberries that appear ripe
3. Skip images with no ripe strawberries
4. Use the web tool: `python3 scripts/label_images_web.py model/datasets/manual_ripeness_to_label`

## 🚀 After Labeling
Train a multi-class ripeness detection model:
- Class 0: ripe (your manual labels)
- Class 1: unripe (from Kaggle)
- Class 2: overripe (from Kaggle)

This will give your robotic picker ripeness awareness!
