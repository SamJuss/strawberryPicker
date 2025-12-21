#!/usr/bin/env python3
"""
Retrain model with expanded dataset (139 images) including negative examples
"""

from ultralytics import YOLO

def train_improved_model():
    print("="*70)
    print("TRAINING IMPROVED MODEL WITH NEGATIVE EXAMPLES")
    print("="*70)
    print("Dataset: 139 images (95 strawberry + 44 negative)")
    print("Split: 66 train, 19 val, 10 test")
    print("Goal: Reduce false positives (body parts, red objects)")
    print("="*70)
    
    # Load pretrained model
    model = YOLO('yolov8n.pt')
    
    # Train with stronger regularization and augmentation
    results = model.train(
        data='model/dataset_homemade_labeled/data.yaml',
        epochs=50,  # Fewer epochs since we have more data
        imgsz=640,
        batch=8,
        name='homemade_yolov8n_v2_negatives',
        project='model/detection',
        
        # Stronger augmentation for more variety
        hsv_h=0.03,      # More color variation (default: 0.015)
        hsv_s=0.9,       # More saturation (default: 0.7)
        hsv_v=0.6,       # More brightness (default: 0.4)
        degrees=15,      # Rotation +/- 15 degrees (default: 0)
        translate=0.2,   # Translation (default: 0.1)
        scale=0.6,       # Scaling (default: 0.5)
        fliplr=0.5,      # Horizontal flip
        flipud=0.2,      # Add vertical flips (default: 0)
        
        # Lower learning rate for fine-tuning
        lr0=0.001,       # Initial learning rate (default: 0.01)
        lrf=0.001,       # Final learning rate (default: 0.01)
        
        # Stronger regularization to prevent overfitting
        weight_decay=0.001,  # Increased from default 0.0005
        
        # Early stopping
        patience=10,
        
        # Save best only
        save_period=0,
        
        # Device
        device=0,
        
        # Cache for faster training
        cache=True,
        
        # Deterministic training
        deterministic=True,
        
        # Close mosaic at epoch 10 (helps with negative examples)
        close_mosaic=10,
    )
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE!")
    print("="*70)
    print(f"Model saved: model/detection/homemade_yolov8n_v2_negatives/weights/best.pt")
    print(f"Results saved: model/detection/homemade_yolov8n_v2_negatives/")
    print("="*70)
    
    return results

if __name__ == '__main__':
    train_improved_model()