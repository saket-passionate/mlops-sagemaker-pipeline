import gradio as gr
import os
import sys
import json

sys.path.append(os.path.abspath(".."))

from sagemaker.predictor import Predictor
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer
from ml_pipeline.pipeline import get_session

region = 'ca-central-1'
bucket = 'mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp'
endpoint_name = 'mlops-endpoint'

sagemaker_session = get_session(region, bucket=bucket)

predictor = Predictor(
    endpoint_name=endpoint_name,
    sagemaker_session=sagemaker_session,
    serializer=JSONSerializer(),
    deserializer=JSONDeserializer()
)

def predict(input_json):
    print("Raw Gradio input:", input_json)

    try:
        data = json.loads(input_json)   # THIS FIXES THE ISSUE
    except Exception as e:
        return f"Invalid JSON format: {e}"

    print("Parsed JSON:", data)
    prediction = predictor.predict(data)
    return str(prediction)

iface = gr.Interface(
    fn=predict,
    inputs=gr.Textbox(lines=4, placeholder='[{"island": "Fiji", "gender": "female", "age": 28}]'),
    outputs="text",
    title="MLOps Model Prediction",
    description="Enter JSON input to get prediction",
)

if __name__ == "__main__":
    iface.launch()
