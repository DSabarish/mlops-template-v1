"""
Standard cleaning: drop nulls, drop duplicates, validate schema.
"""
import pandas as pd
from config import FEATURE_COLUMNS, TARGET_COLUMN


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw data: require columns, drop nulls, drop duplicates."""
    required = FEATURE_COLUMNS + [TARGET_COLUMN]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}. Expected {required}")
    df = df[required].copy()
    df = df.dropna()
    df = df.drop_duplicates()
    return df


if __name__ == "__main__":
    from gcs_ingestion import query_bq
    df = query_bq()
    df = clean(df)
    print("Cleaned shape:", df.shape)
