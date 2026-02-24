"""
Generate data: 100 records, 5 feature columns, 1 target.
"""
import os
import pandas as pd
import numpy as np
from config import FEATURE_COLUMNS, TARGET_COLUMN


def generate_data(n_records: int = 100, seed: int = 42) -> pd.DataFrame:
    """Generate n_records with 5 features and 1 target (linear-ish relation)."""
    rng = np.random.default_rng(seed)
    n = n_records
    X = rng.uniform(0, 10, size=(n, 5))
    coefs = np.array([1.0, 0.5, 0.3, 0.2, 0.1])
    y = X @ coefs + rng.normal(0, 0.5, size=n)
    df = pd.DataFrame(X, columns=FEATURE_COLUMNS)
    df[TARGET_COLUMN] = y
    return df


if __name__ == "__main__":
    df = generate_data(100)
    print("Shape:", df.shape)
    print(df.head())
    out = os.path.join(os.path.dirname(__file__), "data", "data.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_csv(out, index=False)
    print("Wrote", out)
