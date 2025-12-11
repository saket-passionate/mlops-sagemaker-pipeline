import json
import boto3

s3_client = boto3.client('s3')
sm_client = boto3.client('sagemaker', region_name='ca-central-1')
bucket_name = 'mlopspipelinestack-mlopsmodelbucket88eed9f0-lzsbdgp0dgqy'

PIPELINE_NAME = "MlOPsPipeline"

def handler(event, context):


    sm_client.start_pipeline_execution(PipelineName=PIPELINE_NAME)


    return {
        'statusCode': 200,
        'body': json.dumps('Trigger Sagemaker Pipeline Successfully')
    }
