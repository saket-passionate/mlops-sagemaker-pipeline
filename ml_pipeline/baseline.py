from sagemaker.model_monitor.dataset_format import DatasetFormat
from sagemaker.model_monitor.model_monitoring import DefaultModelMonitor
import sagemaker
import boto3


region = 'ca-central-1'
role = 'arn:aws:iam::252312373833:role/MlopsPipelineStack-SageMakerExecutionRole7843F3B8-84gSLJ2pWKPJ'  # Replace with your SageMaker role ARN
bucket = 'mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp' 

def get_session(region: str = "ca-central-1", bucket: str = "") -> sagemaker.session.Session:
    """
    Creates and returns a SageMaker session for the specified AWS region.
    Optionally specifies a default S3 bucket.
    """
    boto_session = boto3.Session(region_name=region)
    sagemaker_client = boto_session.client("sagemaker")

    return sagemaker.session.Session(
        boto_session=boto_session,
        sagemaker_client=sagemaker_client,
        default_bucket=bucket,
    )


def run_monitoring():

    monitor = DefaultModelMonitor(
        role=role,
        sagemaker_session=get_session(region='ca-central-1', bucket=bucket),
        instance_count=1,
        instance_type='ml.t3.large',
        volume_size_in_gb=20,
        max_runtime_in_seconds=3600
        )
    monitor.suggest_baseline(
        baseline_dataset="s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/processing/output/train.csv",
        dataset_format=DatasetFormat.csv(),
        output_s3_uri="s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/monitoring/baseline/"

    )

if __name__ == "__main__":
    run_monitoring()
