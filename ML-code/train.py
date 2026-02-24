"""
Train model and save to GCS: latest/ plus versioned folder (old models kept).
"""
import os
import joblib
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from config import (
    ARTIFACTS_BUCKET,
    MODELS_GCS_PREFIX,
    MODEL_FILENAME,
    LATEST_SUBFOLDER,
    PROJECT_ID,
)


def train(X, y):
    """Fit LinearRegression; return model and metrics dict."""
    model = LinearRegression()
    model.fit(X, y)
    pred = model.predict(X)
    return model, {"mse": mean_squared_error(y, pred), "r2": r2_score(y, pred)}


def save_local(model, path: str = None) -> str:
    """Save model as joblib locally."""
    path = path or os.path.join(os.path.dirname(__file__), "models", MODEL_FILENAME)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    return path


def upload_to_gcs(local_path: str, gcs_prefix: str, subfolder: str) -> str:
    """Upload local file to GCS at prefix/subfolder/MODEL_FILENAME. Returns gs:// URI."""
    from google.cloud import storage
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(ARTIFACTS_BUCKET)
    blob_path = f"{gcs_prefix}/{subfolder}/{os.path.basename(local_path)}"
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(local_path, content_type="application/octet-stream")
    return f"gs://{ARTIFACTS_BUCKET}/{blob_path}"


def train_and_save_to_gcs(X, y) -> tuple:
    """
    Train, save locally, upload to GCS at models/latest/ and models/v_<timestamp>/.
    Returns (model, local_path, latest_uri, version_uri, metrics).
    """
    model, metrics = train(X, y)
    local_path = save_local(model)
    version = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    latest_uri = upload_to_gcs(local_path, MODELS_GCS_PREFIX, LATEST_SUBFOLDER)
    version_uri = upload_to_gcs(local_path, MODELS_GCS_PREFIX, f"v_{version}")
    return model, local_path, latest_uri, version_uri, metrics


if __name__ == "__main__":
    from clean import clean
    from transformation import transform
    from gcs_ingestion import query_bq
    df = clean(query_bq())
    X, y = transform(df)
    _, _, latest_uri, version_uri, metrics = train_and_save_to_gcs(X, y)
    print("Latest:", latest_uri)
    print("Versioned:", version_uri)
    print("Metrics:", metrics)
