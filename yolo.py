import os
import json
import base64
from io import BytesIO
from PIL import Image
import numpy as np
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

# Create blueprint for YOLO analysis
yolo_bp = Blueprint('yolo', __name__)

# Mock YOLO model class for demonstration
class MockYOLOModel:
    """
    Mock YOLO model for demonstration purposes.
    In a real implementation, this would load an actual YOLOv5 model.
    """
    
    def __init__(self):
        self.class_names = [
            "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
            "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
            "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
            "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee"
        ]
    
    def predict(self, image):
        """
        Mock prediction function.
        In a real implementation, this would run the actual YOLO model.
        """
        # Simulate some detections for demonstration
        height, width = image.shape[:2]
        
        # Mock detections (in real scenario, these would come from the model)
        mock_detections = [
            {
                "class_id": 0,  # person
                "confidence": 0.95,
                "x_center": 0.5,
                "y_center": 0.4,
                "width": 0.2,
                "height": 0.6
            },
            {
                "class_id": 2,  # car
                "confidence": 0.88,
                "x_center": 0.7,
                "y_center": 0.7,
                "width": 0.3,
                "height": 0.2
            }
        ]
        
        # Convert to the expected format
        results = []
        for det in mock_detections:
            x_center = det["x_center"]
            y_center = det["y_center"]
            w = det["width"]
            h = det["height"]
            
            # Convert to pixel coordinates
            x_min = int((x_center - w/2) * width)
            y_min = int((y_center - h/2) * height)
            x_max = int((x_center + w/2) * width)
            y_max = int((y_center + h/2) * height)
            
            results.append({
                "class_name": self.class_names[det["class_id"]],
                "class_id": det["class_id"],
                "confidence": det["confidence"],
                "box_2d": {
                    "x_min": x_min,
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max
                }
            })
        
        return results

# Initialize mock model
model = MockYOLOModel()

@yolo_bp.route('/analyze', methods=['POST'])
@cross_origin()
def analyze_image():
    """
    Analyze an uploaded image using YOLO object detection.
    
    Expected input:
    - image: base64 encoded image or file upload
    
    Returns:
    - JSON with detection results
    """
    try:
        # Check if image is provided
        if 'image' not in request.files and 'image_data' not in request.json:
            return jsonify({
                "error": "No image provided. Please upload an image file or provide base64 image data."
            }), 400
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            # Read and process the image
            image = Image.open(file.stream)
            image_name = file.filename
        
        # Handle base64 image data
        elif 'image_data' in request.json:
            image_data = request.json['image_data']
            # Remove data URL prefix if present
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            image_name = "uploaded_image.jpg"
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array for processing
        image_array = np.array(image)
        
        # Run YOLO prediction
        detections = model.predict(image_array)
        
        # Prepare response
        response = {
            "status": "success",
            "image_name": image_name,
            "image_dimensions": {
                "width": image.width,
                "height": image.height
            },
            "detections": detections,
            "detection_count": len(detections),
            "processing_info": {
                "model": "YOLOv5 (Mock)",
                "framework": "PyTorch",
                "optimization": "Enabled"
            }
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "message": "Failed to process image. Please ensure the image is valid."
        }), 500

@yolo_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "model": "YOLOv5 (Mock)",
        "version": "1.0.0"
    }), 200

@yolo_bp.route('/classes', methods=['GET'])
@cross_origin()
def get_classes():
    """Get available object classes."""
    return jsonify({
        "classes": model.class_names,
        "total_classes": len(model.class_names)
    }), 200

