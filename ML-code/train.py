"""
Train model and save to GCS only: latest/ plus versioned folder (old models kept).
No local model files.
"""
import joblib
from io import BytesIO
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


def _upload_model_bytes_to_gcs(model_bytes: bytes, gcs_prefix: str, subfolder: str) -> str:
    """Upload model bytes to GCS at prefix/subfolder/MODEL_FILENAME. Returns gs:// URI."""
    from google.cloud import storage
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(ARTIFACTS_BUCKET)
    blob_path = f"{gcs_prefix}/{subfolder}/{MODEL_FILENAME}"
    blob = bucket.blob(blob_path)
    blob.upload_from_string(model_bytes, content_type="application/octet-stream")
    return f"gs://{ARTIFACTS_BUCKET}/{blob_path}"


def train_and_save_to_gcs(X, y) -> tuple:
    """
    Train and save to GCS only (models/latest/ and models/v_<timestamp>/).
    Returns (model, latest_uri, version_uri, metrics).
    """
    model, metrics = train(X, y)
    buf = BytesIO()
    joblib.dump(model, buf)
    model_bytes = buf.getvalue()
    version = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    latest_uri = _upload_model_bytes_to_gcs(model_bytes, MODELS_GCS_PREFIX, LATEST_SUBFOLDER)
    version_uri = _upload_model_bytes_to_gcs(model_bytes, MODELS_GCS_PREFIX, f"v_{version}")
    return model, latest_uri, version_uri, metrics


if __name__ == "__main__":
    from clean import clean
    from transformation import transform
    from gcs_ingestion import query_bq
    df = clean(query_bq())
    X, y = transform(df)
    _, latest_uri, version_uri, metrics = train_and_save_to_gcs(X, y)
    print("Latest:", latest_uri)
    print("Versioned:", version_uri)
    print("Metrics:", metrics)
