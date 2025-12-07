

# This is inference script it should load model
# Preprocess in coming input 
# Run Prediction

import joblib
import os
import json
import numpy as np
import pandas as pd


## 1. LOAD MODEL AT CONTAINER STARTUP

def model_fn(model_dir):
    model_path = os.path.join(model_dir, "model.joblib")
    preprocessor_path = os.path.join(model_dir, "preprocessing_pipeline.joblib")
    print(f"Loading model from {model_path}")

    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)

    print({"model": model, "preprocessor": preprocessor})

    return {"model": model, "preprocessor": preprocessor}

## 2. Process INPUT

def input_fn(request_body, content_type):
    """
    Deserialize the request body into numpy array for model prediction
    
    """

    ### Request body sample
    ## 5.1,3.5,6.2,7.8
    # island, gender,age

    if content_type == "text/csv":
        # Convert CSV string -> numpy array

        data = np.array(
            [
                list(map(float, row.split(",")))
                for row in request_body.strip().split("\n")
            ]
        )
        return data
    
    elif content_type == "application/json":
        data = request_body
        print("The incoming data is: ", type(data))
        
        import json
        data = json.loads(data)
        print("The data after json.loads() is: ", data)
        
        df= pd.DataFrame(data)
        X = df[["island", "gender", "age"]]
        print("The output data frame is: ", X)
        

    return X


    


def predict_fn(input_data, model_data):
    """
    Perform prediction using the loaded model
    
    """
    preprocessor = model_data["preprocessor"]
    model = model_data["model"]
    print("Input data is: ", input_data)
    
    X_transformed = preprocessor.transform(input_data)
    print("X_transformed is:", X_transformed)
    
    prediction = model.predict(X_transformed)
    print("Model prediction is: ", X_transformed)
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
