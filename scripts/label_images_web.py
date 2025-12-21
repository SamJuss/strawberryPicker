#!/usr/bin/env python3
"""
Web-based image labeling tool for WSL environments.
Run this script and open the provided URL in your browser.

Usage:
    python3 scripts/label_images_web.py model/dataset_homemade

Then open http://localhost:5000 in your browser
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory
from pathlib import Path
import base64
import json
from PIL import Image
import io

app = Flask(__name__)

class WebLabeler:
    def __init__(self, image_dir, class_names):
        self.image_dir = Path(image_dir)
        self.class_names = class_names
        self.images = sorted([f for f in self.image_dir.glob('*.jpg')
                             if not f.name.endswith(':Zone.Identifier')])
        self.current_idx = 0
        self.labels = {}
        
        # Load existing labels
        self.load_existing_labels()
        
    def load_existing_labels(self):
        """Load any existing label files"""
        for img_path in self.images:
            label_path = img_path.with_suffix('.txt')
            if label_path.exists():
                with open(label_path, 'r') as f:
                    boxes = []
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            class_id = int(parts[0])
                            x_center = float(parts[1])
                            y_center = float(parts[2])
                            width = float(parts[3])
                            height = float(parts[4])
                            boxes.append({
                                'class_id': class_id,
                                'x_center': x_center,
                                'y_center': y_center,
                                'width': width,
                                'height': height
                            })
                    self.labels[img_path.name] = boxes
    
    def get_current_image(self):
        """Get the current image as base64"""
        if self.current_idx >= len(self.images):
            return None
        
        img_path = self.images[self.current_idx]
        
        # Convert image to base64
        with open(img_path, 'rb') as f:
            img_data = f.read()
            img_base64 = base64.b64encode(img_data).decode()
        
        # Get image dimensions
        with Image.open(img_path) as img:
            width, height = img.size
        
        return {
            'filename': img_path.name,
            'data': img_base64,
            'width': width,
            'height': height,
            'index': self.current_idx,
            'total': len(self.images)
        }
    
    def save_labels(self, filename, boxes):
        """Save labels in YOLO format"""
        label_path = self.image_dir / f"{filename}.txt"
        
        with open(label_path, 'w') as f:
            for box in boxes:
                f.write(f"{box['class_id']} {box['x_center']} {box['y_center']} {box['width']} {box['height']}\n")
        
        self.labels[filename] = boxes
        print(f"Saved {len(boxes)} boxes for {filename}")
    
    def next_image(self):
        """Move to next image"""
        self.current_idx = min(self.current_idx + 1, len(self.images) - 1)
        return self.get_current_image()
    
    def prev_image(self):
        """Move to previous image"""
        self.current_idx = max(self.current_idx - 1, 0)
        return self.get_current_image()
    
    def get_progress(self):
        """Get labeling progress"""
        labeled = sum(1 for img in self.images if img.with_suffix('.txt').exists())
        return {
            'current': self.current_idx + 1,
            'total': len(self.images),
            'labeled': labeled,
            'percentage': (labeled / len(self.images)) * 100
        }

# Global labeler instance
labeler = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Image Labeling Tool</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f0f0f0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .progress {
            background-color: #e0e0e0;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        .progress-bar {
            background-color: #4CAF50;
            height: 20px;
            border-radius: 5px;
            transition: width 0.3s;
        }
        .image-container {
            position: relative;
            display: inline-block;
            border: 2px solid #ddd;
            cursor: crosshair;
            max-width: 100%;
        }
        .image-container img {
            max-width: 100%;
            height: auto;
            display: block;
        }
        .box {
            position: absolute;
            border: 2px solid #00ff00;
            background-color: rgba(0, 255, 0, 0.1);
            pointer-events: none;
        }
        .box-label {
            position: absolute;
            background-color: #00ff00;
            color: black;
            padding: 2px 5px;
            font-size: 12px;
            font-weight: bold;
            pointer-events: none;
        }
        .controls {
            margin-top: 20px;
            text-align: center;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #45a049;
        }
        button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        .info {
            margin-top: 20px;
            padding: 10px;
            background-color: #e8f4f8;
            border-radius: 5px;
        }
        .instructions {
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .instructions h3 {
            margin-top: 0;
        }
        .instructions ul {
            margin-bottom: 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Strawberry Image Labeling Tool</h1>
        
        <div class="progress">
            <div>Image <span id="current">1</span> of <span id="total">31</span></div>
            <div>Progress: <span id="labeled">0</span> / <span id="total-images">31</span> labeled (<span id="percentage">0</span>%)</div>
            <div class="progress-bar" id="progress-bar" style="width: 0%"></div>
        </div>
        
        <div class="instructions">
            <h3>Instructions:</h3>
            <ul>
                <li>Click and drag on the image to draw a bounding box around each strawberry</li>
                <li>Click "Save & Next" to save labels and move to the next image</li>
                <li>Click "Previous" to go back to the previous image</li>
                <li>Click "Reset Boxes" to clear all boxes for the current image</li>
                <li>Boxes are automatically saved when you click "Save & Next"</li>
            </ul>
        </div>
        
        <div style="text-align: center;">
            <div class="image-container" id="image-container">
                <img id="image" src="" alt="Loading..." draggable="false">
            </div>
        </div>
        
        <div class="controls">
            <button id="prev-btn" onclick="previousImage()">Previous</button>
            <button id="reset-btn" onclick="resetBoxes()">Reset Boxes</button>
            <button id="save-btn" onclick="saveAndNext()">Save & Next</button>
        </div>
        
        <div class="info">
            <strong>Current Image:</strong> <span id="filename">-</span><br>
            <strong>Boxes:</strong> <span id="box-count">0</span>
        </div>
    </div>

    <script>
        let currentBoxes = [];
        let isDrawing = false;
        let startX, startY;
        let currentImageData = null;
        
        // Get image container and image element
        const imageContainer = document.getElementById('image-container');
        const img = document.getElementById('image');
        
        // Prevent image dragging
        img.addEventListener('dragstart', function(e) {
            e.preventDefault();
        });
        
        // Mouse event handlers
        imageContainer.addEventListener('mousedown', function(e) {
            // Only start drawing if clicking on the container or image
            if (e.target !== imageContainer && e.target !== img) return;
            
            const rect = img.getBoundingClientRect();
            startX = e.clientX - rect.left;
            startY = e.clientY - rect.top;
            isDrawing = true;
            e.preventDefault();
        });
        
        imageContainer.addEventListener('mousemove', function(e) {
            if (!isDrawing) return;
            
            const rect = img.getBoundingClientRect();
            const currentX = e.clientX - rect.left;
            const currentY = e.clientY - rect.top;
            
            // Remove existing temporary box
            const tempBox = document.getElementById('temp-box');
            if (tempBox) tempBox.remove();
            
            // Draw temporary box
            const box = document.createElement('div');
            box.id = 'temp-box';
            box.className = 'box';
            box.style.left = Math.min(startX, currentX) + 'px';
            box.style.top = Math.min(startY, currentY) + 'px';
            box.style.width = Math.abs(currentX - startX) + 'px';
            box.style.height = Math.abs(currentY - startY) + 'px';
            box.style.borderColor = '#ffff00';
            imageContainer.appendChild(box);
            e.preventDefault();
        });
        
        imageContainer.addEventListener('mouseup', function(e) {
            if (!isDrawing) return;
            isDrawing = false;
            
            // Remove temporary box
            const tempBox = document.getElementById('temp-box');
            if (tempBox) tempBox.remove();
            
            const rect = img.getBoundingClientRect();
            const endX = e.clientX - rect.left;
            const endY = e.clientY - rect.top;
            
            // Calculate box coordinates relative to image
            const x = Math.min(startX, endX);
            const y = Math.min(startY, endY);
            const width = Math.abs(endX - startX);
            const height = Math.abs(endY - startY);
            
            // Only add if box has reasonable size
            if (width > 10 && height > 10) {
                addBox(x, y, width, height);
            }
            e.preventDefault();
        });
        
        // Also handle mouse leave
        imageContainer.addEventListener('mouseleave', function(e) {
            if (isDrawing) {
                isDrawing = false;
                const tempBox = document.getElementById('temp-box');
                if (tempBox) tempBox.remove();
            }
        });
        
        function addBox(x, y, width, height) {
            const box = {
                x: x,
                y: y,
                width: width,
                height: height,
                class_id: 0
            };
            
            currentBoxes.push(box);
            drawBoxes();
            updateBoxCount();
        }
        
        function drawBoxes() {
            // Remove existing boxes
            const existingBoxes = document.querySelectorAll('.box, .box-label');
            existingBoxes.forEach(box => box.remove());
            
            // Draw all boxes
            currentBoxes.forEach((box, index) => {
                // Draw box
                const boxDiv = document.createElement('div');
                boxDiv.className = 'box';
                boxDiv.style.left = box.x + 'px';
                boxDiv.style.top = box.y + 'px';
                boxDiv.style.width = box.width + 'px';
                boxDiv.style.height = box.height + 'px';
                imageContainer.appendChild(boxDiv);
                
                // Draw label
                const labelDiv = document.createElement('div');
                labelDiv.className = 'box-label';
                labelDiv.style.left = box.x + 'px';
                labelDiv.style.top = (box.y - 20) + 'px';
                labelDiv.textContent = 'strawberry ' + (index + 1);
                imageContainer.appendChild(labelDiv);
            });
        }
        
        function updateBoxCount() {
            document.getElementById('box-count').textContent = currentBoxes.length;
        }
        
        function loadImage() {
            fetch('/api/current-image')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                        return;
                    }
                    
                    currentImageData = data;
                    img.src = 'data:image/jpeg;base64,' + data.data;
                    document.getElementById('filename').textContent = data.filename;
                    document.getElementById('current').textContent = data.index + 1;
                    document.getElementById('total').textContent = data.total;
                    
                    // Load existing boxes
                    currentBoxes = [];
                    if (data.existing_boxes) {
                        // Convert normalized coordinates to pixel coordinates
                        data.existing_boxes.forEach(box => {
                            const pixelBox = {
                                x: box.x_center * img.width - (box.width * img.width) / 2,
                                y: box.y_center * img.height - (box.height * img.height) / 2,
                                width: box.width * img.width,
                                height: box.height * img.height,
                                class_id: box.class_id
                            };
                            currentBoxes.push(pixelBox);
                        });
                    }
                    
                    drawBoxes();
                    updateBoxCount();
                    updateProgress();
                });
        }
        
        function saveAndNext() {
            // Convert boxes to normalized coordinates
            const normalizedBoxes = currentBoxes.map(box => {
                return {
                    class_id: box.class_id,
                    x_center: (box.x + box.width / 2) / img.width,
                    y_center: (box.y + box.height / 2) / img.height,
                    width: box.width / img.width,
                    height: box.height / img.height
                };
            });
            
            fetch('/api/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filename: currentImageData.filename,
                    boxes: normalizedBoxes
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    nextImage();
                } else {
                    alert('Error saving labels: ' + data.error);
                }
            });
        }
        
        function nextImage() {
            fetch('/api/next')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert('All images labeled!');
                        return;
                    }
                    currentBoxes = [];
                    loadImage();
                });
        }
        
        function previousImage() {
            fetch('/api/prev')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert('This is the first image');
                        return;
                    }
                    currentBoxes = [];
                    loadImage();
                });
        }
        
        function resetBoxes() {
            currentBoxes = [];
            drawBoxes();
            updateBoxCount();
        }
        
        function updateProgress() {
            fetch('/api/progress')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('labeled').textContent = data.labeled;
                    document.getElementById('total-images').textContent = data.total;
                    document.getElementById('percentage').textContent = data.percentage.toFixed(1);
                    document.getElementById('progress-bar').style.width = data.percentage + '%';
                });
        }
        
        // Load first image on page load
        window.onload = function() {
            loadImage();
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/current-image')
def get_current_image():
    image_data = labeler.get_current_image()
    if image_data is None:
        return jsonify({'error': 'No more images'})
    
    # Add existing boxes if any
    if image_data['filename'] in labeler.labels:
        image_data['existing_boxes'] = labeler.labels[image_data['filename']]
    
    return jsonify(image_data)

@app.route('/api/next')
def next_image():
    image_data = labeler.next_image()
    if image_data is None:
        return jsonify({'error': 'No more images'})
    return jsonify(image_data)

@app.route('/api/prev')
def prev_image():
    image_data = labeler.prev_image()
    if image_data is None:
        return jsonify({'error': 'This is the first image'})
    return jsonify(image_data)

@app.route('/api/save', methods=['POST'])
def save_labels():
    try:
        data = request.json
        filename = data['filename']
        boxes = data['boxes']
        
        labeler.save_labels(filename, boxes)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/progress')
def get_progress():
    return jsonify(labeler.get_progress())

def main():
    global labeler
    
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/label_images_web.py <image_directory>")
        sys.exit(1)
    
    image_dir = sys.argv[1]
    class_names = ['strawberry']
    
    labeler = WebLabeler(image_dir, class_names)
    
    print(f"\n" + "="*60)
    print("WEB LABELING TOOL STARTED")
    print("="*60)
    print(f"Found {len(labeler.images)} images to label")
    print("\nOpen your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()