"""
Standard transformation: produce feature matrix X and target y for training.
"""
import pandas as pd
from config import FEATURE_COLUMNS, TARGET_COLUMN


def transform(df: pd.DataFrame):
    """From cleaned DataFrame return (X, y) for sklearn."""
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]
    return X, y


if __name__ == "__main__":
    from clean import clean
    from gcs_ingestion import query_bq
    df = clean(query_bq())
    X, y = transform(df)
    print("X shape:", X.shape, "y shape:", y.shape)
