import os
import pandas as pd
import shutil
from sklearn.linear_model import LinearRegression
import joblib  # use joblib directly, not from sklearn.externals


if __name__ == "__main__":
    # SageMaker sets this environment variable to input training data channel path
    train_dir = os.environ.get('SM_CHANNEL_TRAIN') or "/opt/ml/input/data/train"

    train_data_path = os.path.join(train_dir, "train.csv")
    print(f"Loading training data from {train_data_path}")

    preprocessing_pipeline_path = os.path.join(train_dir, "preprocessing_pipeline.joblib")
    print(f"Loading preprocessing pipeline from: {preprocessing_pipeline_path}")
    preprocessing_pipeline = joblib.load(preprocessing_pipeline_path)
    
    df = pd.read_csv(train_data_path, header=None)

    # Assuming last column is the label
    X_train = df.iloc[:, :-1]
    y_train = df.iloc[:, -1]
    print("Head of X_train is: ", X_train.head())
    print("Head of y_train is: ", y_train.head())

    # Train a logistic regression model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # SageMaker sets this environment variable as model artifact path for saving
    model_dir = os.environ.get('SM_MODEL_DIR') or "/opt/ml/model"
    model_output_path = os.path.join(model_dir, "model.joblib")
    preprocessing_pipeline_output_path = os.path.join(model_dir, "preprocessing_pipeline.joblib")

    print(f"Saving model to {model_output_path}")
    joblib.dump(model, model_output_path)

    print(f"Saving preprocessing pipeline to {preprocessing_pipeline_output_path} ")
    joblib.dump(preprocessing_pipeline, preprocessing_pipeline_output_path)

    

