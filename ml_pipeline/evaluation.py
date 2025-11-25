import os
import tarfile
import joblib
import json
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score

if __name__ == "__main__":
    # Path where SageMaker places the model artifact (.tar.gz)
    model_tar_path = "/opt/ml/processing/model/model.tar.gz"

    # Extract model archive
    with tarfile.open(model_tar_path) as tar:
        tar.extractall(path="/opt/ml/processing/model")
    print("Model archive extracted")

    # Load the sklearn model file (assuming model.joblib saved in training script)
    model_path = "/opt/ml/processing/model/model.joblib"
    model = joblib.load(model_path)
    print("Model loaded from:", model_path)

    # Load evaluation dataset (expected by your pipeline)
    eval_data_path = "/opt/ml/processing/train/train.csv"  # adjust path as needed
    df = pd.read_csv(eval_data_path, header=None)

    # Split features and targets (last column assumed target)
    X_eval = df.iloc[:, :-1]
    y_eval = df.iloc[:, -1]

    # Predict using the loaded model
    y_pred = model.predict(X_eval)

    # Compute regression metrics
    rmse = mean_squared_error(y_eval, y_pred, squared=False)
    r2 = r2_score(y_eval, y_pred)

    # Create evaluation report
    report = {
        "regression_metrics": {
            "rmse": {"value": rmse, "standard_deviation": "NaN"},
            "r2": {"value": r2, "standard_deviation": "NaN"}
        }
    }

    print("Evaluation report:", report)

    # Save the evaluation report to a JSON file expected by SageMaker pipeline
    evaluation_output_dir = "/opt/ml/processing/evaluation"
    os.makedirs(evaluation_output_dir, exist_ok=True)
    report_path = os.path.join(evaluation_output_dir, "evaluation.json")

    with open(report_path, "w") as f:
        f.write(json.dumps(report))
    print(f"Saved evaluation report to {report_path}")
