# 🍓 StrawberryPicker - AI-Powered Robotic Harvesting System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-green.svg)](https://github.com/ultralytics/ultralytics)

An intelligent robotic system for automated strawberry harvesting using computer vision and machine learning.

## 🌟 Features

- **AI-Powered Detection**: Real-time strawberry detection using YOLOv8
- **Ripeness Classification**: 4-class ripeness detection (unripe, ripe, overripe, stem)
- **Robotic Control**: Arduino-based robotic arm with inverse kinematics
- **Real-time Processing**: Live camera feed analysis and robotic coordination
- **Model Training Pipeline**: Comprehensive training and validation system
- **Hugging Face Integration**: Pre-trained models available on Hugging Face

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Arduino IDE (for robotic arm control)
- USB camera
- Arduino-compatible board (e.g., Arduino Uno, ESP32)

### Installation

```bash
# Clone the repository
git clone https://github.com/theonegareth/strawberryPicker.git
cd strawberryPicker

# Install dependencies
pip install -r requirements.txt

# Validate setup
python scripts/setup_training.py --validate-only
```

## 📁 Project Structure

```
strawberryPicker/
├── scripts/                 # Python scripts for training and inference
├── src/                     # Source code modules
├── model/                   # Trained models and datasets
├── ArduinoCode/             # Arduino robotic arm control
├── assets/                  # Images, CAD models, and resources
├── huggingface_models/      # Hugging Face model repository
├── docs/                    # Documentation
└── requirements.txt         # Python dependencies
```

## 🤖 Usage

### Training Models

```bash
# Train YOLOv8 model
python scripts/train_yolov8.py --data model/dataset_stem_label/data.yaml --epochs 150

# Train ripeness classifier
python scripts/train_ripeness_classifier.py --dataset model/ripeness_manual_dataset
```

### Real-time Detection

```bash
# Webcam inference
python webcam_inference.py

# Arduino robotic control
python src/strawberry_picker_pipeline.py
```

### Arduino Setup

1. Open `ArduinoCode/inverse kinematics/src/main.cpp` in Arduino IDE
2. Upload to your Arduino board
3. Connect servos according to the pin definitions
4. Use serial commands: `I x y z` for inverse kinematics or `F t0 t1 t2` for forward kinematics

## 📊 Model Performance

- **YOLOv8s**: 95.2% mAP@0.5 for strawberry detection
- **Ripeness Classifier**: 91.71% accuracy across 4 classes
- **Real-time Processing**: 30+ FPS on Raspberry Pi 4

## 🔧 Configuration

Edit `src/config.py` to customize:
- Camera settings
- Robotic arm parameters
- Model paths
- Detection thresholds

## 📈 Training Workflow

See [TRAINING_WORKFLOW.md](TRAINING_WORKFLOW.md) for detailed training procedures and best practices.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ultralytics** - YOLOv8 framework and documentation
- **Roboflow** - Dataset management and annotation tools
- **Arduino Community** - Open-source hardware ecosystem
- **Raspberry Pi Foundation** - Edge computing platform
