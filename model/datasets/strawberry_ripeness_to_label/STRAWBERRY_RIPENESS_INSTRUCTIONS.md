# 🍓 STRAWBERRY RIPENESS LABELING INSTRUCTIONS

## 📊 Dataset Overview
- **Total Images**: 75
- **Categories**: ripe, unripe, overripe
- **Fruit Type**: Strawberries Only
- **Purpose**: Robotic strawberry harvesting with ripeness awareness

## 🎯 Labeling Goal
Create perfect bounding boxes for **strawberry ripeness detection** to enable your robotic picker to harvest only perfectly ripe strawberries.

## 📋 Ripeness Categories for Strawberries

### **🟢 UNRIPE STRAWBERRIES** (Class 0)
- **Color**: Green, white, or pale pink
- **Texture**: Hard, firm, underdeveloped
- **Size**: Smaller, not fully grown
- **Appearance**: Pointed shape, no red coloration
- **When to label**: Not ready for harvest

### **🟡 RIPE STRAWBERRIES** (Class 1) 
- **Color**: Bright red, uniform color
- **Texture**: Firm but yielding, smooth surface
- **Size**: Full size, plump appearance
- **Appearance**: Rounded shape, glossy surface
- **When to label**: **PERFECT FOR HARVESTING**

### **🔴 OVERRIPE STRAWBERRIES** (Class 2)
- **Color**: Dark red, purple, or brown spots
- **Texture**: Soft, mushy, or wrinkled
- **Appearance**: Sunken areas, dull surface
- **Signs**: Beginning to decay, loss of firmness
- **When to label**: Past optimal harvest time

## ✅ Labeling Instructions

### **🔍 What to Look For:**
1. **Focus on strawberries only** - ignore other fruits in multi-fruit images
2. **Draw tight bounding boxes** around each strawberry
3. **Multiple strawberries per image** - label each one individually
4. **Mixed ripeness** - use different categories for different berries

### **🖱️ Web Tool Controls:**
- **Click & drag** to draw bounding boxes
- **Save & Next** to save and proceed
- **Reset Boxes** to clear current image
- **Previous** to go back

### **⚡ Quick Category Guide:**
- **1 key**: Unripe (green/white)
- **2 key**: Ripe (bright red) ← **TARGET FOR HARVESTING**
- **3 key**: Overripe (dark/soft)
- **S key**: Skip difficult images
- **Q key**: Quit and save

## 🚀 After Labeling

### **Training Command:**
```bash
python3 scripts/train_strawberry_ripeness_model.py
```

### **Expected Classes:**
- **Class 0**: unripe (avoid harvesting)
- **Class 1**: ripe ← **TARGET FOR ROBOTIC PICKING**
- **Class 2**: overripe (avoid harvesting)

## 🎊 Benefits for Robotic Harvesting

### **🤖 Robotic Intelligence**
- **Precision picking**: Only harvest ripe strawberries
- **Quality control**: Avoid unripe/overripe ones
- **Optimal timing**: Perfect ripeness selection
- **Efficiency**: Automated ripeness classification

### **📈 Harvesting Strategy**
- **Greenhouse automation**: Smart harvesting robots
- **Quality assurance**: Consistent ripeness standards
- **Profit maximization**: Harvest at peak ripeness
- **Waste reduction**: Avoid premature or overripe picking

## 🎯 Perfect Ripeness Indicators
Look for strawberries that are:
- **Bright red color** throughout
- **Firm but slightly yielding** to gentle pressure
- **Glossy surface** with fresh appearance
- **Full size** and plump shape
- **No green or white patches**
- **No soft spots or wrinkles**

**🍓🤖 Your robotic picker will have perfect ripeness intelligence for optimal strawberry harvesting!**