from sagemaker.model_monitor.dataset_format import DatasetFormat
from sagemaker.model_monitor.model_monitoring import DefaultModelMonitor


region = 'ca-central-1'
role = 'arn:aws:iam::252312373833:role/MlopsPipelineStack-SageMakerExecutionRole7843F3B8-84gSLJ2pWKPJ'  # Replace with your SageMaker role ARN
bucket = 'mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp' 




def run_monitoring():

    monitor = DefaultModelMonitor(
        role=role,

        instance_count=1,
        instance_type='ml.m5.xlarge',
        volume_size_in_gb=20,
        max_runtime_in_seconds=3600
        )
    monitor.suggest_baseline(
        baseline_dataset="s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/processing/output/train.csv",
        dataset_format=DatasetFormat.csv(),
        output_s3_uri="s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/monitoring/input/"

    )

if __name__ == "__main__":
    run_monitoring()
