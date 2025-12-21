import subprocess
import sys
import os


# Verify version
import sagemaker
print(f"SageMaker version: {sagemaker.__version__}")

import boto3
print(f"Boto3 version: {boto3.__version__}")

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import joblib
from datetime import datetime
from sagemaker.feature_store.feature_group import FeatureGroup


print("Processing step started")
import logging
logging.basicConfig(level=logging.INFO)
logging.info("Logging enabled")

region = 'ca-central-1'
bucket = 'mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp'

def get_session(region: str = "ca-central-1", bucket: str = "") -> sagemaker.session.Session:
    """
    Creates and returns a SageMaker session for the specified AWS region.
    Optionally specifies a default S3 bucket.
    """
    boto_session = boto3.Session(region_name=region)
    sagemaker_client = boto_session.client("sagemaker")

    return sagemaker.session.Session(
        boto_session=boto_session,
        sagemaker_client=sagemaker_client,
        default_bucket=bucket,
    )

def run_preprocessing():
    input_data_path = os.path.join("/opt/ml/processing/input", "toronto_telematics_realistic.csv")
    
    df = pd.read_csv(input_data_path)

    print("Loaded dataframe:\n", df.head())

    # Separate features + target
    X = df.drop(columns=['timestamp', 'trip_score'])
    y = df["trip_score"]

    # Separate numerical and cateogorical features
    numeric_features = ['speed', 'acceleration', 'rpm', 'fuel_rate', 'engine_temp', 'driver_age', 'driver_safety_score']
    categorical_features = ['vehicle_type', 'road_type', 'weather', 'driver_gender', 'driver_style']

    driver_features = df[['driver_id', 'driver_age',
                        'driver_gender', 'driver_style', 'driver_safety_score']].drop_duplicates(subset=["driver_id"])
    
    driver_features["event_time"] = datetime.utcnow().isoformat()
    session = get_session(region=region, bucket=bucket)
    print("Sagemaker session is: ", session)

    # Ingest features into Feature Store (Do not Create)
    """
    sagemaker_session = get_session(region, bucket=bucket)
    fg = FeatureGroup(
        name="driver_features_fg",
        sagemaker_session=sagemaker_session
    )

    fg.ingest(
        data_frame=driver_features,
        max_workers=4,
        wait=True
    )
    """

    print("======Ingested Features into Offline Feature Store======")

    print("X head:\n", X.head())
    print("y head:\n", y.head())
    
    numeric_preprocessor = Pipeline(
        steps=[
            ("imputation_mean", SimpleImputer(missing_values=np.nan, strategy="mean")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_preprocessor = Pipeline(
        steps=[
            (
                "imputation_constant",
                SimpleImputer(fill_value="missing", strategy="constant"),
            ),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )


    preprocessor = ColumnTransformer(
        [
            ("categorical", categorical_preprocessor, categorical_features),
            ("numerical", numeric_preprocessor, numeric_features),
        ]
    )

    pipeline = make_pipeline(preprocessor)
    processed_data = pipeline.fit_transform(X)
    print("The preprocessed data is: ", processed_data)
    
    # Make sure output directory exists
    print("The shape of nd arrray processed data is: " ,processed_data.shape)
    output_dir = "/opt/ml/processing/train"
    os.makedirs(output_dir, exist_ok=True)

    # Convert to DataFrame
    if hasattr(processed_data, "toarray"):  # sparse matrix from OneHotEncoder
        processed_df = pd.DataFrame(processed_data.toarray())
    else:
        processed_df = pd.DataFrame(processed_data)
    
    # Add target column back
    processed_df["trip_score"] = y
    print("Processed DataFrame with target:\n", processed_df.head())

    import joblib
    # Save the fitted preprocessing pipeline
    joblib.dump(pipeline, os.path.join(output_dir, "preprocessing_pipeline.joblib"))


    # Save processed data as CSV; convert numpy array back to dataframe if needed
    processed_df.to_csv(
        os.path.join(output_dir, "train.csv"),
        index=False
    )

    print("Processed data is: ", processed_data)
    return processed_data

if __name__ == "__main__":

    run_preprocessing()
    print("Processing job completed successfully.")
    
    