# Manual Bounding Box Labeling Guide

## 🎯 Purpose
You are manually annotating bounding boxes for the reduced Kaggle dataset to ensure perfect quality for robotic strawberry picking.

## 📊 Dataset Info
- Total images to label: 50
- Selection method: diverse
- Output directory: model/datasets/manual_labeled

## 🔧 Labeling Instructions

### 1. Bounding Box Requirements
- **Tight Fit**: Box should closely follow strawberry contours
- **Complete Coverage**: Entire strawberry must be inside the box
- **No Background**: Minimize background pixels in the box
- **Individual Berries**: Each strawberry gets its own box

### 2. Quality Standards
- **Position Accuracy**: Box center should align with berry center
- **Size Appropriateness**: Box should be ~5-10% larger than berry
- **Edge Alignment**: Box edges should follow berry shape
- **Consistency**: Similar quality across all images

### 3. Common Issues to Avoid
- **Loose Boxes**: Too much background space
- **Tight Boxes**: Cutting off parts of strawberries
- **Merged Berries**: Multiple berries in one box
- **Partial Coverage**: Boxes not fully enclosing berries

## 🛠️ Labeling Tools

### Recommended Tools:
1. **LabelImg** (Open source)
2. **CVAT** (Computer Vision Annotation Tool)
3. **Roboflow** (Online platform)
4. **Custom web tool** (if available)

### Label Format:
- **YOLO Format**: class_id x_center y_center width height
- **Normalized Coordinates**: 0-1 range
- **Single Class**: All strawberries are class 0

## 📋 Quality Checklist

Before finalizing each label:
- [ ] Box tightly encloses entire strawberry
- [ ] No parts of strawberry cut off
- [ ] Minimal background pixels
- [ ] Box follows berry shape reasonably well
- [ ] Consistent with other labels in dataset

## 🎯 Success Criteria

**Excellent Labels:**
- Tight fit around strawberry
- Complete coverage
- Minimal background
- Consistent quality

**Acceptable Labels:**
- Reasonable fit
- Full strawberry visible
- Not too much background
- Consistent with dataset

**Needs Improvement:**
- Loose fitting
- Partial coverage
- Too much background
- Inconsistent quality

## 🚀 Next Steps

1. **Label all images** in the reduced dataset
2. **Quality review** of all annotations
3. **Train new model** with manually labeled data
4. **Test performance** on robotic picking
5. **Iterate improvements** based on results

## 📊 Expected Outcome

With manual annotation, we expect:
- **Higher accuracy**: Better bounding box positioning
- **Improved precision**: More reliable robotic picking
- **Better generalization**: Consistent quality across conditions
- **Reduced errors**: Fewer picking failures

## 💡 Tips for Success

- **Take your time**: Quality over speed
- **Be consistent**: Similar approach for all images
- **Check examples**: Review good vs poor labels
- **Test frequently**: Validate with small batches
- **Iterate**: Improve based on robotic performance

---

**Remember**: High-quality manual annotation will significantly improve your robotic strawberry picking accuracy!
