"""
Vertex AI custom job entrypoint: heavy lifting (clean + transform + train, save to GCS).
Run as the main script inside a Vertex AI custom training job.
Expects env: GCP_PROJECT, ARTIFACTS_BUCKET, DATA_BUCKET, DATASET_ID, TABLE_ID (or input from job args).
"""
import os
import argparse
from config_loader import load_config

_cfg = load_config()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-uri", default=None, help="gs:// bucket/path to data CSV (else query BQ)")
    args = parser.parse_args()
    PROJECT_ID = _cfg["project_id"]
    ARTIFACTS_BUCKET = _cfg["artifacts_bucket"]
    DATASET_ID = _cfg["dataset_id"]
    TABLE_ID = _cfg["table_id"]
    if args.data_uri:
        import pandas as pd
        from google.cloud import storage
        path = args.data_uri.replace("gs://", "").split("/", 1)
        bucket_name, blob_name = path[0], path[1]
        client = storage.Client(project=os.environ.get("GCP_PROJECT", PROJECT_ID))
        blob = client.bucket(bucket_name).blob(blob_name)
        local = "/tmp/data.csv"
        blob.download_to_filename(local)
        df = pd.read_csv(local)
    else:
        from gcs_ingestion import query_bq
        df = query_bq()
    from clean import clean
    from transformation import transform
    from train import train_and_save_to_gcs
    df = clean(df)
    X, y = transform(df)
    _, latest_uri, version_uri, metrics = train_and_save_to_gcs(X, y)
    print("Latest:", latest_uri)
    print("Versioned:", version_uri)
    print("Metrics:", metrics)


if __name__ == "__main__":
    main()
