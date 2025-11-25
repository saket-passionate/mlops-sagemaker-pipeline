import boto3
import sagemaker
from pipeline import get_pipeline  # Replace with your pipeline script filename without .py

def main():
    region = 'ca-central-1'
    role = 'arn:aws:iam::252312373833:role/MlopsPipelineStack-SageMakerExecutionRole7843F3B8-84gSLJ2pWKPJ'  # Replace with your SageMaker role ARN
    bucket = 'mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp'  # Replace with your S3 bucket for pipeline artifacts
    
    # Get the pipeline instance
    pipeline = get_pipeline(region, role=role, bucket=bucket)
    
    # Create or update the pipeline on SageMaker
    pipeline.upsert(role_arn=role)
    print(f"Pipeline {pipeline.name} is created/updated.")
    
    # Start execution of the pipeline
    execution = pipeline.start()
    print(f"Pipeline execution started with ARN: {execution.arn}")
    
    # Wait for the execution to complete (optional)
    execution.wait()
    print("Pipeline execution completed.")
    
    # Optional: List execution steps and their status
    steps = execution.list_steps()
    for step in steps:
        print(f"Step: {step['StepName']}, Status: {step['StepStatus']}")

if __name__ == "__main__":
    main()
