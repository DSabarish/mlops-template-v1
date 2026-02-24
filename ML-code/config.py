"""
ML pipeline config. Values come from Terraform outputs (env in CI/CD).
"""
import os

# GCP (from Terraform outputs)
PROJECT_ID = os.environ.get("GCP_PROJECT", "sabs-20")
REGION = os.environ.get("GCP_REGION", "asia-south1")

# Buckets (Terraform: data_bucket, artifacts_bucket)
DATA_BUCKET = os.environ.get("DATA_BUCKET", "mlapp-dev-data-sabs-20")
ARTIFACTS_BUCKET = os.environ.get("ARTIFACTS_BUCKET", "mlapp-dev-artifacts-sabs-20")

# BigQuery (Terraform: dataset_id, table_id)
DATASET_ID = os.environ.get("DATASET_ID", "training_dataset_dev")
TABLE_ID = os.environ.get("TABLE_ID", "features_table")

# Schema: f1..f5 = features, T = target
FEATURE_COLUMNS = ["f1", "f2", "f3", "f4", "f5"]
TARGET_COLUMN = "T"

# GCS paths (versioned)
DATA_GCS_PREFIX = "data"
MODELS_GCS_PREFIX = "models"
MODEL_FILENAME = "model.joblib"
LATEST_SUBFOLDER = "latest"

# Local paths
MODEL_DIR = "models"
