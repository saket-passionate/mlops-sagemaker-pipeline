import gradio as gr
import os
import sys

sys.path.append(os.path.abspath(".."))

from sagemaker.predictor import Predictor
from sagemaker.serializers import CSVSerializer
from sagemaker.deserializers import JSONDeserializer
from ml_pipeline.pipeline import get_session

# SageMaker setup
region = 'ca-central-1'
bucket = 'mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp'
endpoint_name = 'mlops-endpoint'
role = 'arn:aws:iam::252312373833:role/MlopsPipelineStack-SageMakerExecutionRole7843F3B8-84gSLJ2pWKPJ'

sagemaker_session = get_session(region, bucket=bucket)

predictor = Predictor(
    endpoint_name=endpoint_name,
    sagemaker_session=sagemaker_session,
    serializer=CSVSerializer(),      
    deserializer=JSONDeserializer()  
)

# Prediction function for Gradio
def predict(input_csv):
    # input_csv is a comma-separated string from the user
    prediction = predictor.predict(input_csv)
    return str(prediction)

# Build Gradio interface
iface = gr.Interface(
    fn=predict,
    inputs=gr.Textbox(lines=2, placeholder="Enter CSV input, e.g., 0.2,1.0,12.0,..."),
    outputs="text",
    title="MLOps Model Prediction",
    description="Enter comma-separated feature values to get prediction from SageMaker endpoint."
)

if __name__ == "__main__":
    iface.launch()
