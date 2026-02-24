"""
Save data to BigQuery table (Terraform-created).
"""
import pandas as pd
from config_loader import load_config

_cfg = load_config()
PROJECT_ID = _cfg["project_id"]
DATASET_ID = _cfg["dataset_id"]
TABLE_ID = _cfg["table_id"]


def save_to_bq(df: pd.DataFrame) -> str:
    """Load DataFrame into BigQuery table. Returns table ref."""
    from google.cloud import bigquery

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    job = client.load_table_from_dataframe(df, table_ref)
    job.result()
    return table_ref


if __name__ == "__main__":
    from generate_data import generate_data
    df = generate_data(100)
    ref = save_to_bq(df)
    print("Saved to", ref)
