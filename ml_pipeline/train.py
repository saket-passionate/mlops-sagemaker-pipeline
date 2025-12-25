import os
import pandas as pd
import shutil
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import joblib  # use joblib directly, not from sklearn.externals


if __name__ == "__main__":
    # SageMaker sets this environment variable to input training data channel path
    print(os.environ.get('SM_CHANNEL_TRAIN'))
    train_dir = os.environ.get('SM_CHANNEL_TRAIN') or "/opt/ml/data/train/"

    train_data_path = os.path.join(train_dir, "train.csv")
    print(f"Loading training data from {train_data_path}")

    preprocessing_pipeline_path = os.path.join(train_dir, "preprocessing_pipeline.joblib")
    print(f"Loading preprocessing pipeline from: {preprocessing_pipeline_path}")
    preprocessing_pipeline = joblib.load(preprocessing_pipeline_path)
    
    df = pd.read_csv(train_data_path)

    # Assuming last column is the label
    # Separate features + label
    X_train = df.drop(columns=["trip_score"])
    y_train = df["trip_score"].astype(float)   # must be numeric

    print("Head of X_train:")
    print(X_train.head())

    print("Head of y_train:")
    print(y_train.head())

    # Train RandomForest model
    model = RandomForestRegressor(n_estimators=5, max_depth=3, random_state=42)
    model.fit(X_train, y_train)

    # SageMaker sets this environment variable as model artifact path for saving
    model_dir = os.environ.get('SM_MODEL_DIR') or "/opt/ml/model"
    model_output_path = os.path.join(model_dir, "model.joblib")
    preprocessing_pipeline_output_path = os.path.join(model_dir, "preprocessing_pipeline.joblib")

    print(f"Saving model to {model_output_path}")
    joblib.dump(model, model_output_path)

    print(f"Saving preprocessing pipeline to {preprocessing_pipeline_output_path} ")
    joblib.dump(preprocessing_pipeline, preprocessing_pipeline_output_path)

    

