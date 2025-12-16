import os
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import joblib


print("Processing step started")
import logging
logging.basicConfig(level=logging.INFO)
logging.info("Logging enabled")

def run_preprocessing():
    input_data_path = os.path.join("/opt/ml/processing/input", "toronto_telematics_realistic.csv")
    
    df = pd.read_csv(input_data_path)

    print("Loaded dataframe:\n", df.head())

    # Separate features + target
    X = df.drop(columns=['timestamp', 'trip_score'])
    y = df["trip_score"]

    # Separate numerical and cateogorical features
    numeric_features = ['speed', 'acceleration', 'rpm', 'fuel_rate', 'engine_temp']
    categorical_features = ['vehicle_type', 'road_type', 'weather', 'driver_id', 'driver_style']

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
    
    