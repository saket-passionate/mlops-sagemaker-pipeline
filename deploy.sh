#!/bin/bash
set -e
set -x  # Print commands as they run for easier debugging

# Optionally create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install AWS CDK CLI locally in this environment (no global install)
npm install aws-cdk

echo "Packaging Lambda Function"
cd lambda_inference
pip install -r requirements.txt -t .
zip -r ../lambda_package.zip .
cd ..

echo "Uploading ML Scripts"
cd ml_pipeline
aws s3 cp preprocess.py s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/processing/input/code/preprocess.py
aws s3 cp evaluation.py s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/evaluation/input/code/evaluation.py
aws s3 cp train.py s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/training/input/code/train.py
cd ..

echo "Deploying CDK Stack"
cd cloud_infra
cdk synth
cdk deploy --require-approval never
cd ..

echo "Running SageMaker Pipeline"
python ml_pipeline/run_pipeline.py

echo "Build and Deployment Completed Successfully!"
