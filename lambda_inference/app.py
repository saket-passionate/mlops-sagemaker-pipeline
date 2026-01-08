import json
import boto3

s3_client = boto3.client('s3')
sm_client = boto3.client('sagemaker')
bucket_name = 'mlopspipelinestack-mlopsmodelbucket88eed9f0-lzsbdgp0dgqy'

endpoint_name = 'mlops-endpoint'
endpoint_config_name = 'mlops-endpoint'
model_name = 'mlops-island-model'


def get_latest_model_package_arn(model_package_group_name):
    response = sm_client.list_model_packages(
        ModelPackageGroupName=model_package_group_name,
        MaxResults=100,
        SortBy='CreationTime',
        SortOrder='Descending'
    )
    model_package_arn = response['ModelPackageSummaryList'][0]['ModelPackageArn']
    return model_package_arn


def handler(event, context):
    # Load your model (example: from /opt/model.joblib if included via Layer)

    response = s3_client.list_objects_v2(Bucket=bucket_name)
    print("list of objects in bucket are: ", response)
    

    model_package_group_name = event['detail']['ModelPackageGroupName']   
    model_package_arn = get_latest_model_package_arn(model_package_group_name)

    

    sm_client.create_model(
        ModelName=model_name,
        PrimaryContainer={"ModelPackageName": model_package_arn},
        ExecutionRoleArn="arn:aws:iam::252312373833:role/MlopsPipelineStack-SageMakerExecutionRole7843F3B8-84gSLJ2pWKPJ"
)

    
    # 1️⃣ Create a new endpoint configuration

    # Set Data Capture Configurations
    capture_modes = ["Input", "Output"]
    s3_capture_upload_path = "s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/monitoring/data_capture/"
    
    sm_client.create_endpoint_config(
        EndpointConfigName=endpoint_config_name,
        ProductionVariants=[
            {
                "VariantName": "AllTraffic",
                "ModelName": model_name,
                "InitialInstanceCount": 1,
                "InstanceType": "ml.t2.medium",
                "InitialVariantWeight": 1
            }
        ],
        DataCaptureConfig= {
            'EnableCapture': True,
            'InitialSamplingPercentage' : 50,
            'DestinationS3Uri': s3_capture_upload_path,
            'CaptureOptions': [{"CaptureMode" : capture_mode} for capture_mode in capture_modes] # Example - Use list comprehension to capture both Input and Output
    }
    )

    # Update the endpoint to use the new model package
    sm_client.create_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=endpoint_config_name
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Model Endpoint Deployment Success')
    }
