"""
Get data from BigQuery (query) and save to GCS bucket (infra), versioned.
"""
import os
from datetime import datetime
from config_loader import load_config

_cfg = load_config()
PROJECT_ID = _cfg["project_id"]
DATASET_ID = _cfg["dataset_id"]
TABLE_ID = _cfg["table_id"]
DATA_BUCKET = _cfg["data_bucket"]
DATA_GCS_PREFIX = _cfg["data_gcs_prefix"]


def query_bq(query: str = None):
    """Run BigQuery query and return DataFrame."""
    from google.cloud import bigquery
    client = bigquery.Client(project=PROJECT_ID)
    if query is None:
        query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`"
    return client.query(query).to_dataframe()


def save_to_gcs(df, bucket: str = None, prefix: str = None, version: str = None) -> str:
    """Save DataFrame as CSV to GCS with version folder. Returns gs:// path."""
    import pandas as pd
    from google.cloud import storage
    bucket = bucket or DATA_BUCKET
    prefix = prefix or DATA_GCS_PREFIX
    version = version or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = f"{prefix}/{version}/data.csv"
    client = storage.Client(project=PROJECT_ID)
    b = client.bucket(bucket)
    blob = b.blob(path)
    blob.upload_from_string(df.to_csv(index=False), content_type="text/csv")
    return f"gs://{bucket}/{path}"


def bq_to_gcs(query: str = None, version: str = None) -> str:
    """Query BQ and save result to GCS (versioned). Returns GCS URI."""
    df = query_bq(query)
    return save_to_gcs(df, version=version)


if __name__ == "__main__":
    uri = bq_to_gcs()
    print("Saved to", uri)
