#!/bin/bash
set -e

echo "Installing CDK + tooling"
pip install -r requirements.txt
npm install -g aws-cdk

echo "Packaging Lambda Function"
cd lambda_inference
pip install -r requirements.txt -t .
zip -r ../lambda_package.zip .
cd ..

echo "Uploading ML Scripts"
aws s3 cp ml/processing/preprocess.py s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/processing/input/code/preprocess.py
aws s3 cp ml/evaluation/evaluation.py s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/evaluation/input/code/evaluation.py
aws s3 cp ml/training/train.py s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/training/input/code/train.py

echo "Deploy CDK Stack"
cd cloud_infra
cdk synth
cdk deploy --require-approval never
cd ..

echo "Updating SageMaker Pipeline"
python ml_pipeline/run_pipeline.py

echo "COMPUTE ACTION COMPLETE!"
