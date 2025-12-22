# 🍓 STRAWBERRY RIPENESS LABELING GUIDE

## 📊 Dataset Overview
- **Total Images**: 75
- **Categories**: ripe, unripe, overripe
- **Source**: Complete Fruit Ripeness Dataset
- **Purpose**: Perfect ripeness detection for robotic strawberry harvesting

## 🎯 Labeling Goal
Create precise bounding boxes around **strawberries only** to train a multi-class ripeness detection model.

## 📋 Ripeness Categories Guide

### 🟢 **Unripe Strawberries** (Class 0)
- **Color**: Green, white, or very pale pink
- **Texture**: Hard, firm to touch
- **Size**: Smaller, underdeveloped
- **Appearance**: No red coloration, may have green patches
- **Harvest Status**: **NOT READY** - too early

### 🟡 **Ripe Strawberries** (Class 1) 
- **Color**: Bright, uniform red
- **Texture**: Firm but not hard, slight give when pressed
- **Size**: Full size, plump and developed
- **Appearance**: Vibrant red color, glossy surface
- **Harvest Status**: **PERFECT** - optimal picking time

### 🔴 **Overripe Strawberries** (Class 2)
- **Color**: Dark red, purple, or brown spots
- **Texture**: Soft, mushy, or wrinkled
- **Appearance**: Sunken areas, dull surface, possible mold
- **Shape**: May be misshapen or collapsing
- **Harvest Status**: **TOO LATE** - past optimal time

## ✅ Labeling Instructions

### **🖱️ Web Tool Controls:**
- **Click & drag** to draw tight bounding boxes
- **Number keys (1,2,3)** to select ripeness category
- **Save & Next** to save and proceed
- **Reset Boxes** to clear current image
- **Previous** to go back if needed

### **📏 Box Drawing Tips:**
1. **Draw tight boxes** - hug the strawberry outline closely
2. **Include entire berry** - don't cut off any parts
3. **Multiple berries** - label each strawberry individually
4. **Mixed ripeness** - use different categories for different berries
5. **Partial berries** - only label if >50% visible

### **🎯 What to Label:**
- ✅ **Whole strawberries** with clear ripeness characteristics
- ✅ **Multiple strawberries** in same image (different boxes)
- ✅ **Partially visible** berries if ripeness is clear
- ❌ **Other fruits** (apples, bananas, etc.) - skip these
- ❌ **Very blurry** or unclear images
- ❌ **Tiny strawberries** (<10% of image)

### **🔍 Quick Category Selection:**
- **Press 1**: Unripe (green/white)
- **Press 2**: Ripe (bright red) 
- **Press 3**: Overripe (dark/rotting)
- **Press S**: Skip difficult images

## 🚀 After Labeling

### **Training Command:**
```bash
python3 scripts/train_strawberry_ripeness_model.py
```

### **Expected Performance:**
- **3-class ripeness detection**: unripe, ripe, overripe
- **Precision harvesting**: Only pick ripe strawberries
- **Quality control**: Avoid unripe/overripe ones
- **Robotic automation**: Perfect for greenhouse harvesting

## 🎊 Benefits for Your Robotic Picker

### **🤖 Smart Harvesting:**
- **Optimal timing**: Pick only perfectly ripe berries
- **Quality assurance**: Consistent ripeness selection
- **Efficiency**: Automated ripeness classification
- **Profit maximization**: Harvest at peak value

### **🧠 AI Intelligence:**
- **Multi-class detection**: Distinguish all ripeness levels
- **Real-time processing**: Fast ripeness assessment
- **Adaptable**: Works in various lighting conditions
- **Scalable**: Handle multiple berries simultaneously

---

**🍓🤖 Your robotic strawberry picker will have complete ripeness intelligence!**
**Perfect for automated greenhouse harvesting with optimal quality control!**