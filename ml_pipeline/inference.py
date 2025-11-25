

# This is inference script it should load model
# Preprocess in coming input 
# Run Prediction

import joblib
import os
import json
import numpy as np


## 1. LOAD MODEL AT CONTAINER STARTUP

def model_fn(model_dir):
    model_path = os.path.join(model_dir, "model.joblib")
    print(f"Loading model from {model_path}")

    model = joblib.load(model_path)

    return model

## 2. Process INPUT

def input_fn(request_body, content_type):
    """
    Deserialize the request body into numpy array for model prediction
    
    """

    ### Request body sample
    ## 5.1,3.5,6.2,7.8

    if content_type == "text/csv":
        # Convert CSV string -> numpy array

        data = np.array(
            [
                list(map(float, row.split(",")))
                for row in request_body.strip().split("\n")
            ]
        )
        return data
    
    return ValueError(f"Unsupported content type: {content_type}")

def predict_fn(input_data, model):
    """
    Perform prediction using the loaded model
    
    """

    prediction = model.predict(input_data)
    return prediction


def output_fn(prediction, accept):
    """
    Return model predictions in the required response format.
    """
    if accept == "application/json":
        return json.dumps(prediction.tolist()), accept

    if accept == "text/csv":
        csv_output = "\n".join([str(p) for p in prediction])
        return csv_output, accept

    raise ValueError(f"Unsupported accept type: {accept}")
