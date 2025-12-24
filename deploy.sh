#!/bin/bash
set -e
set -x  # Print commands as they run for easier debugging

# Optionally create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

echo "============== PYTHON DEBUG INFO (INSIDE VENV) =============="
echo "Python interpreter (inside venv):"
which python
which python3
python --version

echo "PATH (inside venv):"
echo $PATH
echo "=============================================================="

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
aws s3 cp toronto_telematics_realistic.csv s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/processing/input/data/
aws s3 cp evaluation.py s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/evaluation/input/code/evaluation.py
aws s3 cp train.py s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/training/input/code/train.py
cd ..

echo "Deploying CDK Stack"
cd cloud_infra
../node_modules/.bin/cdk synth
../node_modules/.bin/cdk deploy --require-approval never
cd ..

cd ml_pipeline
echo "Running SageMaker Pipeline"
python run_pipeline.py

echo "ML System Infrastructure is Setup & Deployed"
