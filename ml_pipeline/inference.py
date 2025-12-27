

# This is inference script it should load model
# Preprocess in coming input 
# Run Prediction

import joblib
import os
import json
import numpy as np
import pandas as pd
import boto3
import json

region = 'ca-central-1'
feature_group_name = "driver_features_fg"

fs_runtime = boto3.client(
    service_name="sagemaker-featurestore-runtime",
    region_name = region
    
)

def get_driver_features_online(driver_id):
    """
    Docstring for get_driver_features_online
    
    :param driver_id: Description

        ...
    'Record': [{'FeatureName': 'TransactionID', 'ValueAsString': '2990130'},
    {'FeatureName': 'isFraud', 'ValueAsString': '0'},
    {'FeatureName': 'TransactionDT', 'ValueAsString': '152647'},
    {'FeatureName': 'TransactionAmt', 'ValueAsString': '75.0'},
    {'FeatureName': 'ProductCD', 'ValueAsString': 'H'},
    {'FeatureName': 'card1', 'ValueAsString': '4577'},
    ...
    """
    response = fs_runtime.get_record(
        FeatureGroupName=feature_group_name,
        RecordIdentifierValueAsString=str(driver_id)
    )
    record = response['Record']
    feature_dict = {}

    # Now I want dictionary of my features
    for feature in record:
        feature_name = feature['FeatureName']
        feature_value = feature['ValueAsString']
        feature_dict[feature_name] = feature_value
    
    for col in ['driver_age', 'driver_safety_score']:
        if col in feature_dict:
            feature_dict[col] = float(feature_dict[col])
    
    del feature_dict['event_time']

    print("The features dictionary from feature store is: ", feature_dict)
    
    return feature_dict

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
        # Input Request has following features
        # ['trip_id', 'speed', 'acceleration','rpm', 'fuel_rate', 'engine_temp','vehicle_type', 'road_type', 'weather', 'driver_id']
        
        
        # For a certain driver Id get driver features from Online Feature Store
        # Using driver id we get 4 features from online feature store at inference time, and add to it to create final X to be fed to model
        driver_features = ['driver_age',
                        'driver_gender', 'driver_style', 'driver_safety_score']
        
        features  = ['trip_id', 'speed', 'acceleration','rpm', 'fuel_rate', 'engine_temp','vehicle_type', 'road_type', 'weather',
                    'driver_id', 'driver_style', 'driver_age', 'driver_gender', 'driver_safety_score']
        driver_features_list = []
        
        for driver_id in df["driver_id"]:
            driver_features = get_driver_features_online(driver_id)
            driver_features_list.append(driver_features)

        driver_df = pd.DataFrame(driver_features_list)
        final_df = pd.concat([df.reset_index(drop=True), driver_df])

        # Then concatenate these features in togethere so be sent to preprocessing pipeline
        #X = df[features]
        X = final_df[features]
        
        print("Final inference dataframe:")
        print(X.head())
        print("Shape:", X.shape)
        

    return X


    


def predict_fn(input_data, model_data):
    """
    Perform prediction using the loaded model
    
    """
    preprocessor = model_data["preprocessor"]
    model = model_data["model"]
    print("Input data is: ", input_data.head())
    print("Input data:", input_data)
    X_transformed = preprocessor.transform(input_data)
    print("Transformed shape:", X_transformed.shape)
    
    prediction = model.predict(X_transformed)
    print("Model prediction is: ", prediction)
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
