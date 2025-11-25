import sys
import os
import sagemaker
from sagemaker import ModelPackage
from sagemaker.serverless.serverless_inference_config import ServerlessInferenceConfig

sys.path.append(os.path.abspath(".."))

from ml_pipeline.pipeline import get_session



if __name__ == "__main__":
    region = 'ca-central-1'
    role = 'arn:aws:iam::252312373833:role/MlopsPipelineStack-SageMakerExecutionRole7843F3B8-84gSLJ2pWKPJ'  
    bucket = 'mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp'  

    model_package_arn = 'arn:aws:sagemaker:ca-central-1:252312373833:model-package/saket-mlops-model-group/5'

    sagemaker_session = get_session(region, bucket=bucket)

    model = ModelPackage(
        role = role,
        model_package_arn=model_package_arn,
        sagemaker_session = sagemaker_session
        
    )
    model.deploy(
        initial_instance_count=1,
        instance_type="ml.m5.large",
        endpoint_name='saket-endpoint',
        serverless_inference_config= ServerlessInferenceConfig(memory_size_in_mb=2048, max_concurrency=5)
            
    )





