import json
import boto3

s3_client = boto3.client('s3')
sm_client = boto3.client('sagemaker')
bucket_name = 'mlopspipelinestack-mlopsmodelbucket88eed9f0-lzsbdgp0dgqy'



def handler(event, context):

    return {
        'statusCode': 200,
        'body': json.dumps('Model Endpoint Deployment Success')
    }
