#!/usr/bin/env python3
"""
Real-time Strawberry Detection and Robotic Control Pipeline
Integrates YOLOv11 detection + ripeness classification + Arduino control
"""

import cv2
import numpy as np
import serial
import time
import json
import logging
from pathlib import Path
from datetime import datetime
import argparse
from ultralytics import YOLO
import torch
from PIL import Image
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StrawberryPickerPipeline:
    def __init__(self, config_path="config.yaml"):
        """Initialize the complete strawberry picking pipeline."""
        self.config = self.load_config(config_path)
        self.setup_models()
        self.setup_serial_communication()
        self.setup_camera()
        
        # State tracking
        self.last_detection_time = 0
        self.detection_cooldown = 2.0  # seconds between detections
        self.current_target = None
        
    def load_config(self, config_path):
        """Load configuration from YAML file."""
        try:
            import yaml
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except:
            # Fallback configuration
            return {
                'detection': {
                    'model_path': 'model/weights/yolo11n_strawberry_detect_v3.pt',
                    'confidence_threshold': 0.5,
                    'image_size': 640
                },
                'ripeness': {
                    'model_path': 'model/ripeness_classifier.pkl',
                    'confidence_threshold': 0.7
                },
                'serial': {
                    'port': '/dev/ttyUSB0',
                    'baudrate': 115200,
                    'timeout': 1.0
                },
                'camera': {
                    'index': 0,
                    'width': 640,
                    'height': 480,
                    'fps': 30
                },
                'robot': {
                    'workspace_bounds': {
                        'x_min': 0, 'x_max': 300,
                        'y_min': 0, 'y_max': 200,
                        'z_min': 50, 'z_max': 150
                    },
                    'pick_offset': 20  # mm below detected position
                }
            }
    
    def setup_models(self):
        """Load detection and classification models."""
        try:
            # Load YOLOv11 detection model
            logger.info("Loading YOLOv11 detection model...")
            self.detection_model = YOLO(self.config['detection']['model_path'])
            
            # Load ripeness classification model
            logger.info("Loading ripeness classification model...")
            with open(self.config['ripeness']['model_path'], 'rb') as f:
                self.ripeness_model = pickle.load(f)
            
            logger.info("Models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def setup_serial_communication(self):
        """Initialize serial communication with Arduino."""
        try:
            logger.info(f"Connecting to Arduino on {self.config['serial']['port']}...")
            self.arduino = serial.Serial(
                port=self.config['serial']['port'],
                baudrate=self.config['serial']['baudrate'],
                timeout=self.config['serial']['timeout']
            )
            time.sleep(2)  # Wait for Arduino to initialize
            
            # Test connection
            self.send_command("PING")
            response = self.read_response()
            if response == "PONG":
                logger.info("Arduino connection established")
            else:
                logger.warning("Arduino connection test failed")
                
        except Exception as e:
            logger.error(f"Error connecting to Arduino: {e}")
            self.arduino = None
    
    def setup_camera(self):
        """Initialize camera for real-time detection."""
        try:
            logger.info("Initializing camera...")
            self.cap = cv2.VideoCapture(self.config['camera']['index'])
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['camera']['width'])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['camera']['height'])
            self.cap.set(cv2.CAP_PROP_FPS, self.config['camera']['fps'])
            
            if not self.cap.isOpened():
                raise Exception("Could not open camera")
                
            logger.info("Camera initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            raise
    
    def send_command(self, command):
        """Send command to Arduino."""
        if self.arduino and self.arduino.is_open:
            try:
                self.arduino.write(f"{command}\n".encode())
                logger.debug(f"Sent command: {command}")
                return True
            except Exception as e:
                logger.error(f"Error sending command: {e}")
                return False
        return False
    
    def read_response(self, timeout=2.0):
        """Read response from Arduino."""
        if self.arduino and self.arduino.is_open:
            try:
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if self.arduino.in_waiting > 0:
                        response = self.arduino.readline().decode().strip()
                        logger.debug(f"Received response: {response}")
                        return response
                return None
            except Exception as e:
                logger.error(f"Error reading response: {e}")
                return None
        return None
    
    def detect_strawberries(self, frame):
        """Detect strawberries in the current frame."""
        try:
            # Run YOLOv11 detection
            results = self.detection_model(
                frame,
                conf=self.config['detection']['confidence_threshold'],
                imgsz=self.config['detection']['image_size'],
                verbose=False
            )
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Extract detection info
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = box.cls[0].cpu().numpy()
                        
                        # Calculate center point
                        center_x = int((x1 + x2) / 2)
                        center_y = int((y1 + y2) / 2)
                        
                        detections.append({
                            'bbox': [x1, y1, x2, y2],
                            'center': [center_x, center_y],
                            'confidence': float(confidence),
                            'class_id': int(class_id)
                        })
            
            return detections
            
        except Exception as e:
            logger.error(f"Error in detection: {e}")
            return []
    
    def classify_ripeness(self, frame, bbox):
        """Classify ripeness of detected strawberry."""
        try:
            # Extract crop from frame
            x1, y1, x2, y2 = map(int, bbox)
            crop = frame[y1:y2, x1:x2]
            
            if crop.size == 0:
                return None, 0.0
            
            # Resize crop to expected input size
            crop_resized = cv2.resize(crop, (224, 224))
            
            # Prepare for classification
            crop_array = np.array(crop_resized).reshape(1, -1)
            
            # Predict ripeness
            prediction = self.ripeness_model.predict(crop_array)[0]
            probabilities = self.ripeness_model.predict_proba(crop_array)[0]
            
            # Get confidence
            confidence = float(np.max(probabilities))
            
            return prediction, confidence
            
        except Exception as e:
            logger.error(f"Error in ripeness classification: {e}")
            return None, 0.0
    
    def pixel_to_robot_coordinates(self, pixel_x, pixel_y, frame_width, frame_height):
        """Transform pixel coordinates to robot workspace coordinates."""
        try:
            bounds = self.config['robot']['workspace_bounds']
            
            # Simple linear mapping (should be calibrated for accuracy)
            robot_x = bounds['x_min'] + (pixel_x / frame_width) * (bounds['x_max'] - bounds['x_min'])
            robot_y = bounds['y_min'] + (pixel_y / frame_height) * (bounds['y_max'] - bounds['y_min'])
            robot_z = bounds['z_max']  # Start at top, will adjust based on depth
            
            return [robot_x, robot_y, robot_z]
            
        except Exception as e:
            logger.error(f"Error in coordinate transformation: {e}")
            return [0, 0, 0]
    
    def pick_strawberry(self, robot_coords, ripeness):
        """Execute picking sequence for a detected strawberry."""
        try:
            logger.info(f"Starting pick sequence for {ripeness} strawberry at {robot_coords}")
            
            # Only pick ripe strawberries
            if ripeness != 'ripe':
                logger.info(f"Skipping {ripeness} strawberry (only picking ripe)")
                return False
            
            # Send pick command to Arduino
            command = f"PICK,{robot_coords[0]:.1f},{robot_coords[1]:.1f},{robot_coords[2]:.1f}"
            
            if self.send_command(command):
                # Wait for pick completion
                response = self.read_response(timeout=10.0)
                if response == "PICK_DONE":
                    logger.info("Pick completed successfully")
                    return True
                else:
                    logger.warning(f"Pick failed or timed out. Response: {response}")
                    return False
            else:
                logger.error("Failed to send pick command")
                return False
                
        except Exception as e:
            logger.error(f"Error in pick sequence: {e}")
            return False
    
    def process_frame(self, frame):
        """Process a single frame for detection and picking."""
        current_time = time.time()
        
        # Rate limiting
        if current_time - self.last_detection_time < self.detection_cooldown:
            return frame
        
        height, width = frame.shape[:2]
        
        # Detect strawberries
        detections = self.detect_strawberries(frame)
        
        for detection in detections:
            bbox = detection['bbox']
            center = detection['center']
            confidence = detection['confidence']
            
            # Classify ripeness
            ripeness, ripeness_conf = self.classify_ripeness(frame, bbox)
            
            if ripeness and ripeness_conf > self.config['ripeness']['confidence_threshold']:
                # Transform to robot coordinates
                robot_coords = self.pixel_to_robot_coordinates(
                    center[0], center[1], width, height
                )
                
                # Execute pick if it's a ripe strawberry
                if ripeness == 'ripe':
                    success = self.pick_strawberry(robot_coords, ripeness)
                    
                    # Update cooldown after pick attempt
                    self.last_detection_time = current_time
                    
                    # Draw detection result
                    color = (0, 255, 0) if success else (0, 0, 255)  # Green for success, red for failure
                else:
                    color = (255, 255, 0)  # Yellow for unripe/overripe
                
                # Draw bounding box and label
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                label = f"{ripeness} ({ripeness_conf:.2f})"
                cv2.putText(frame, label, (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Draw center point
                cv2.circle(frame, tuple(center), 5, color, -1)
                
                logger.info(f"Detected {ripeness} strawberry at {center} with {ripeness_conf:.2f} confidence")
        
        return frame
    
    def run(self):
        """Main pipeline execution loop."""
        logger.info("Starting Strawberry Picker Pipeline...")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    logger.error("Failed to read frame from camera")
                    break
                
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Display result
                cv2.imshow('Strawberry Picker Pipeline', processed_frame)
                
                # Exit on 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            logger.info("Pipeline interrupted by user")
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up resources...")
        
        if hasattr(self, 'cap'):
            self.cap.release()
        
        if hasattr(self, 'arduino') and self.arduino:
            self.arduino.close()
        
        cv2.destroyAllWindows()
        logger.info("Cleanup complete")

def main():
    parser = argparse.ArgumentParser(description='Strawberry Picker Pipeline')
    parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    parser.add_argument('--test-mode', action='store_true', help='Run in test mode without Arduino')
    
    args = parser.parse_args()
    
    try:
        pipeline = StrawberryPickerPipeline(args.config)
        
        if args.test_mode:
            logger.info("Running in test mode (no Arduino connection)")
            pipeline.arduino = None
        
        pipeline.run()
        
    except Exception as e:
        logger.error(f"Failed to start pipeline: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())