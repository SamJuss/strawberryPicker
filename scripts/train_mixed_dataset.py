#!/usr/bin/env python3
"""
Train YOLOv8n on mixed dataset (homemade + Kaggle + negatives)
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

def train_mixed_dataset(data_yaml_path, epochs=50, model_size='yolov8n.pt', name=None):
    """Train YOLOv8 on mixed dataset"""
    from ultralytics import YOLO
    
    # Configuration
    imgsz = 640
    batch = 16
    workers = 4
    project = 'model/detection'
    
    if name is None:
        name = f'mixed_conservative_v2_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    # Check dataset
    if not os.path.exists(data_yaml_path):
        print(f"Error: Dataset config not found at {data_yaml_path}")
        sys.exit(1)
    
    print(f"🍓 Training YOLOv8n on mixed dataset")
    print(f"Data YAML: {data_yaml_path}")
    print(f"Model: {model_size}")
    print(f"Epochs: {epochs}")
    print(f"Image size: {imgsz}")
    print(f"Batch size: {batch}")
    print(f"Project: {project}")
    print(f"Name: {name}")
    
    # Load model
    model = YOLO(model_size)
    
    # Train without early stopping (patience=0)
    results = model.train(
        data=data_yaml_path,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        workers=workers,
        project=project,
        name=name,
        pretrained=True,
        seed=42,
        patience=0,  # No early stopping
        save=True,
        save_period=5,
        val=True,
        device='0',  # Use GPU if available
        # Augmentation
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10.0,
        translate=0.1,
        scale=0.5,
        shear=2.0,
        perspective=0.001,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1,
        copy_paste=0.1,
        # Optimization
        lr0=0.002,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3.0,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        box=7.5,
        cls=0.5,
        dfl=1.5,
        # Additional
        close_mosaic=10,
        amp=True,  # Mixed precision
        dropout=0.0,
        verbose=True
    )
    
    print(f"✅ Training completed. Results saved to {project}/{name}")
    
    # Validate
    val_results = model.val()
    print(f"📊 Validation Results:")
    print(f"   mAP50: {val_results.box.map50:.4f}")
    print(f"   mAP50-95: {val_results.box.map:.4f}")
    
    # Precision and recall
    if hasattr(val_results.box, 'p'):
        precision = val_results.box.p.mean() if hasattr(val_results.box.p, 'mean') else val_results.box.p
        recall = val_results.box.r.mean() if hasattr(val_results.box.r, 'mean') else val_results.box.r
        print(f"   Precision: {precision:.4f}")
        print(f"   Recall: {recall:.4f}")
    
    # Save metrics to a file
    metrics_path = Path(project) / name / 'metrics.txt'
    with open(metrics_path, 'w') as f:
        f.write(f"mAP50: {val_results.box.map50:.4f}\n")
        f.write(f"mAP50-95: {val_results.box.map:.4f}\n")
        if hasattr(val_results.box, 'p'):
            f.write(f"Precision: {precision:.4f}\n")
            f.write(f"Recall: {recall:.4f}\n")
    
    print(f"📄 Metrics saved to {metrics_path}")
    
    # Export to ONNX
    onnx_path = f'{project}/{name}/weights/best.onnx'
    model.export(format='onnx', imgsz=imgsz, dynamic=False)
    print(f"🔧 Model exported to ONNX: {onnx_path}")
    
    return model, val_results

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Train YOLOv8 on mixed dataset')
    parser.add_argument('--data', type=str, default='model/dataset_mixed_conservative_v2/data.yaml',
                       help='Path to data.yaml file')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of training epochs')
    parser.add_argument('--model', type=str, default='yolov8n.pt',
                       help='Model size (yolov8n.pt, yolov8s.pt, etc.)')
    parser.add_argument('--name', type=str, default=None,
                       help='Custom name for this training run')
    
    args = parser.parse_args()
    
    # Train the model
    model, results = train_mixed_dataset(
        data_yaml_path=args.data,
        epochs=args.epochs,
        model_size=args.model,
        name=args.name
    )
    
    print("\n🎯 Next Steps:")
    print("1. Test the model on new images:")
    print(f"   python scripts/test_homemade_model.py --model {results.save_dir}/weights/best.pt")
    print("2. Compare with baseline models:")
    print("   python scripts/test_and_compare_models.py")
    print("3. Deploy the model:")
    print(f"   Update scripts/final_strawberry_detector.py with model path: {results.save_dir}/weights/best.pt")

if __name__ == '__main__':
    main()