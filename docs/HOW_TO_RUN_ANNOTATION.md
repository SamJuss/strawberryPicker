# 🛠️ How to Run the Manual Annotation Tool Yourself

## ✅ **Web Server Stopped Successfully**

The annotation tool has been stopped. Now you can run it yourself whenever you're ready!

## 🚀 **How to Start the Annotation Tool Manually**

### **Method 1: Direct Command (Simplest)**
```bash
# Navigate to your project directory
cd /home/user/machine-learning/GitHubRepos/strawberryPicker

# Start the web labeling tool directly
python3 scripts/label_images_web.py model/datasets/manual_labeled/train/images
```

### **Method 2: Using the Simple Start Script**
```bash
# Navigate to your project directory
cd /home/user/machine-learning/GitHubRepos/strawberryPicker

# Run the simple start script
python3 scripts/start_annotation_simple.py
```

### **Method 3: Manual Setup (Most Control)**
```bash
# Navigate to your project directory
cd /home/user/machine-learning/GitHubRepos/strawberryPicker

# Start the web server manually
python3 -m flask run --host=0.0.0.0 --port=5000
```

## 🌐 **Access the Tool**

**URL**: http://localhost:5000
**Status**: Ready when you see "Running on http://127.0.0.1:5000" in terminal

## 📋 **Step-by-Step Process:**

### **Step 1: Start the Server**
```bash
# Run this command in your terminal:
python3 scripts/label_images_web.py model/datasets/manual_labeled/train/images
```

### **Step 2: Wait for Server to Start**
- You'll see: "Starting Flask development server"
- Then: "Running on http://127.0.0.1:5000"
- The server is ready when you see this message

### **Step 3: Open Your Browser**
1. **Open any web browser** (Chrome, Firefox, Safari, etc.)
2. **Navigate to**: http://localhost:5000
3. **You should see the labeling interface** ready to use

### **Step 4: Start Labeling**
- **Load images** from your reduced Kaggle dataset
- **Draw bounding boxes** around strawberries
- **Save labels** as you go
- **Navigate through images** using the interface

## 🎯 **What You'll See:**

### **Interface Features:**
- **Image display** with your Kaggle images
- **Drawing tools** for creating bounding boxes
- **Navigation controls** to move between images
- **Save functionality** to store your labels
- **Real-time preview** of your annotations

### **Dataset Available:**
- **29 images** from the reduced Kaggle dataset
- **Located in**: `model/datasets/manual_labeled/train/images/`
- **Labels saved to**: `model/datasets/manual_labeled/train/labels/`

## ⏰ **Managing the Server:**

### **To Stop the Server:**
```bash
# Press Ctrl+C in the terminal where it's running
# Or use: pkill -f "python3 scripts/label_images_web.py"
```

### **To Restart Later:**
```bash
# Just run the same command again:
python3 scripts/label_images_web.py model/datasets/manual_labeled/train/images
```

## 🎯 **Quality Standards (Same as Before):**

### **✅ DO:**
- **Draw tight boxes** around each strawberry
- **Include entire visible berry** in the box
- **Make separate boxes** for each individual berry
- **Take your time** - quality over speed

### **❌ DON'T:**
- **Draw loose boxes** with lots of background
- **Cut off parts** of strawberries
- **Put multiple berries** in one box
- **Rush through** the process

## 📊 **Progress Tracking:**

### **Check Your Progress:**
```bash
# Count how many images you've labeled
ls -la model/datasets/manual_labeled/train/labels/ | wc -l

# Check which images still need labeling
ls model/datasets/manual_labeled/train/images/ | head -5
ls model/datasets/manual_labeled/train/labels/ | head -5
```

### **Visual Check:**
```bash
# Create visualization of your progress
python3 scripts/visualize_labels.py --data model/datasets/manual_labeled --output progress_check
```

## 🚀 **Next Steps After Labeling:**

### **Step 1: Complete All Images**
- **Finish labeling all 29 images** with high quality
- **Ensure consistent quality** across all labels

### **Step 2: Stop the Server**
- **Press Ctrl+C** in the terminal to stop the server
- **Your labels are automatically saved**

### **Step 3: Quality Check**
```bash
# Check your labeling statistics
python3 scripts/get_labeling_stats.py --data model/datasets/manual_labeled

# Visualize your labels
python3 scripts/visualize_manual_labels.py --data model/datasets/manual_labeled --output quality_check
```

### **Step 4: Train New Model**
```bash
# Train model on your manually labeled data
python3 scripts/train_manual_labels.py
```

## 🏆 **Success Tips:**

### **Before You Start:**
1. **Set aside 2-4 hours** for quality work
2. **Take regular breaks** to maintain focus
3. **Review the first few images** to establish quality standards
4. **Have good lighting** and a comfortable setup

### **During Labeling:**
1. **Focus on one image at a time**
2. **Double-check each box** before moving on
3. **Maintain consistent quality** throughout
4. **Don't rush** - quality over speed

### **Quality Check:**
1. **Review your first 5 images** completely
2. **Adjust your technique** if needed
3. **Apply lessons learned** to remaining images

---

## 🎯 **Final Reminder:**

**You successfully did this before with your homemade dataset!** The process is identical - just with different (higher quality) images from the Kaggle dataset.

**The tool is ready and waiting for you. Take your time, focus on quality, and you'll create perfect bounding boxes just like you did before!**

## 🏆 **Status:**

**✅ READY TO START MANUAL ANNOTATION**
**🌐 URL**: http://localhost:5000
**📊 Dataset**: 29 Kaggle images ready
**⏰ Time**: 2-4 hours expected
**🎯 Goal**: Perfect bounding boxes for robotic picking

**🎉 RUN THE COMMAND ABOVE AND START LABELING! 🍓🤖**

**You already proved you can do this perfectly - now do it again for the Kaggle images! The tool is ready and waiting for you to start.**