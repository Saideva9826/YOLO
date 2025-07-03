#!/usr/bin/env python3
"""
AWS Lambda Function for YOLO Object Detection

This example demonstrates how to deploy a YOLO model on AWS Lambda.
In a real implementation, you would use an actual YOLOv5 model.
"""

import json
import base64
import boto3
from io import BytesIO
from PIL import Image
import numpy as np

# Mock YOLO model for demonstration
class LambdaYOLOModel:
    """
    Lightweight YOLO model for AWS Lambda deployment.
    In production, this would load an optimized model.
    """
    
    def __init__(self):
        self.class_names = [
            "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
            "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
            "bird", "cat", "dog", "horse", "sheep", "cow"
        ]
    
    def predict(self, image_array):
        """
        Mock prediction for demonstration.
        In production, this would run the actual YOLO inference.
        """
        height, width = image_array.shape[:2]
        
        # Simulate detections based on image characteristics
        detections = []
        
        # Mock detection logic (in real scenario, this would be model inference)
        if width > 500:  # Assume larger images might have cars
            detections.append({
                "class_id": 2,  # car
                "confidence": 0.89,
                "x_center": 0.6,
                "y_center": 0.7,
                "width": 0.25,
                "height": 0.15
            })
        
        if height > 400:  # Assume taller images might have people
            detections.append({
                "class_id": 0,  # person
                "confidence": 0.92,
                "x_center": 0.3,
                "y_center": 0.5,
                "width": 0.15,
                "height": 0.4
            })
        
        # Convert to expected format
        results = []
        for det in detections:
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

# Initialize model (this happens once per Lambda container)
model = LambdaYOLOModel()

def lambda_handler(event, context):
    """
    AWS Lambda handler function for YOLO object detection.
    
    Expected event structure:
    {
        "image_data": "base64_encoded_image_string",
        "image_name": "optional_image_name.jpg"
    }
    
    Returns:
    {
        "statusCode": 200,
        "body": {
            "detections": [...],
            "processing_info": {...}
        }
    }
    """
    
    try:
        # Parse the event
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event
        
        # Extract image data
        image_data = body.get('image_data')
        image_name = body.get('image_name', 'lambda_image.jpg')
        
        if not image_data:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'No image_data provided'
                })
            }
        
        # Remove data URL prefix if present
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
        except Exception as e:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': f'Invalid image data: {str(e)}'
                })
            }
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Run YOLO prediction
        detections = model.predict(image_array)
        
        # Prepare response
        response_body = {
            "status": "success",
            "image_name": image_name,
            "image_dimensions": {
                "width": image.width,
                "height": image.height
            },
            "detections": detections,
            "detection_count": len(detections),
            "processing_info": {
                "model": "YOLOv5-Lambda",
                "framework": "PyTorch",
                "deployment": "AWS Lambda",
                "optimization": "Enabled for serverless"
            }
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_body)
        }
    
    except Exception as e:
        # Log error for debugging
        print(f"Lambda error: {str(e)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }

# For local testing
if __name__ == "__main__":
    # Test the lambda function locally
    test_event = {
        "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
        "image_name": "test.png"
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))

