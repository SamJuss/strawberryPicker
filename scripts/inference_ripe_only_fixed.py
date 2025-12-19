#!/usr/bin/env python3
"""
Inference script for ripe-only strawberry detection.
Uses the trained YOLOv8 model to detect only ripe strawberries.
This version saves output images without requiring GUI.
"""

import argparse
import cv2
import numpy as np
from pathlib import Path
import sys
from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser(description='Ripe-only strawberry detection inference')
    parser.add_argument('--model', type=str, 
                        default='model/detection/ripe_only_yolov8n_quick_20251219_102944/weights/best.pt',
                        help='Path to trained model (default: best.pt from latest training)')
    parser.add_argument('--source', type=str, default='0',
                        help='Source: 0 for webcam, path to image/video, or directory')
    parser.add_argument('--conf', type=float, default=0.5,
                        help='Confidence threshold (default: 0.5)')
    parser.add_argument('--iou', type=float, default=0.45,
                        help='IOU threshold for NMS (default: 0.45)')
    parser.add_argument('--save', action='store_true', default=True,
                        help='Save output images/videos')
    parser.add_argument('--show', action='store_true', default=False,
                        help='Show results in window (may not work in headless environments)')
    parser.add_argument('--device', type=str, default='0',
                        help='Device to run on: 0 for GPU, cpu for CPU')
    parser.add_argument('--output', type=str, default='output',
                        help='Output directory for saved results')
    
    args = parser.parse_args()
    
    # Load model
    print(f"Loading model from {args.model}")
    if not Path(args.model).exists():
        print(f"Error: Model file not found at {args.model}")
        sys.exit(1)
    
    model = YOLO(args.model)
    
    # Determine source
    source = args.source
    if source.isdigit():
        source = int(source)  # webcam index
    
    # Run inference
    results = model.predict(
        source=source,
        conf=args.conf,
        iou=args.iou,
        device=args.device,
        show=args.show,
        save=args.save,
        save_dir=args.output,
        classes=[0],  # only class 0 (ripe)
        verbose=False
    )
    
    # Process results
    for idx, result in enumerate(results):
        if hasattr(result, 'boxes') and result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            confs = result.boxes.conf.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy()
            
            print(f"Result {idx+1}: Detected {len(boxes)} ripe strawberries")
            for i, (box, conf, cls) in enumerate(zip(boxes, confs, classes)):
                x1, y1, x2, y2 = map(int, box)
                print(f"  Strawberry {i+1}: confidence={conf:.3f}, bbox=[{x1},{y1},{x2},{y2}]")
        else:
            print(f"Result {idx+1}: No ripe strawberries detected")
    
    print(f"Inference completed. Results saved to {args.output}")

if __name__ == '__main__':
    main()