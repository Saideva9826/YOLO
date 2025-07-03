#!/bin/bash

# AWS Lambda Deployment Script for YOLO Object Detection
# This script packages and deploys the YOLO function to AWS Lambda

set -e

echo "🚀 AWS Lambda YOLO Deployment Script"
echo "====================================="

# Configuration
FUNCTION_NAME="yolo-object-detection"
RUNTIME="python3.9"
HANDLER="lambda_yolo_function.lambda_handler"
ROLE_NAME="lambda-yolo-execution-role"
REGION="us-east-1"
MEMORY_SIZE=1024
TIMEOUT=30

# Create deployment package
echo "📦 Creating deployment package..."
rm -rf lambda_package
mkdir lambda_package

# Copy function code
cp lambda_yolo_function.py lambda_package/

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r lambda_requirements.txt -t lambda_package/

# Create ZIP package
echo "🗜️ Creating ZIP package..."
cd lambda_package
zip -r ../yolo-lambda-deployment.zip .
cd ..

echo "✅ Deployment package created: yolo-lambda-deployment.zip"

# AWS CLI commands for deployment (commented out for safety)
echo ""
echo "🔧 AWS CLI Deployment Commands:"
echo "================================"
echo ""
echo "1. Create IAM role (if not exists):"
echo "aws iam create-role --role-name $ROLE_NAME \\"
echo "  --assume-role-policy-document '{"
echo "    \"Version\": \"2012-10-17\","
echo "    \"Statement\": ["
echo "      {"
echo "        \"Effect\": \"Allow\","
echo "        \"Principal\": {"
echo "          \"Service\": \"lambda.amazonaws.com\""
echo "        },"
echo "        \"Action\": \"sts:AssumeRole\""
echo "      }"
echo "    ]"
echo "  }'"
echo ""
echo "2. Attach basic execution policy:"
echo "aws iam attach-role-policy --role-name $ROLE_NAME \\"
echo "  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
echo ""
echo "3. Create Lambda function:"
echo "aws lambda create-function \\"
echo "  --function-name $FUNCTION_NAME \\"
echo "  --runtime $RUNTIME \\"
echo "  --role arn:aws:iam::\$(aws sts get-caller-identity --query Account --output text):role/$ROLE_NAME \\"
echo "  --handler $HANDLER \\"
echo "  --zip-file fileb://yolo-lambda-deployment.zip \\"
echo "  --memory-size $MEMORY_SIZE \\"
echo "  --timeout $TIMEOUT \\"
echo "  --region $REGION"
echo ""
echo "4. Update function code (for subsequent deployments):"
echo "aws lambda update-function-code \\"
echo "  --function-name $FUNCTION_NAME \\"
echo "  --zip-file fileb://yolo-lambda-deployment.zip \\"
echo "  --region $REGION"
echo ""
echo "5. Create API Gateway (optional):"
echo "aws apigateway create-rest-api --name yolo-api --region $REGION"
echo ""
echo "📋 Deployment Notes:"
echo "==================="
echo "• Make sure AWS CLI is configured with proper credentials"
echo "• Replace account ID in the role ARN with your actual AWS account ID"
echo "• For production, consider using container images for larger models"
echo "• Monitor Lambda logs in CloudWatch for debugging"
echo "• Set up API Gateway for HTTP access if needed"
echo ""
echo "🎯 Test the function:"
echo "aws lambda invoke \\"
echo "  --function-name $FUNCTION_NAME \\"
echo "  --payload file://test_payload.json \\"
echo "  --region $REGION \\"
echo "  response.json"

