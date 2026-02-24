"""Test clean drops nulls and keeps schema."""
import pandas as pd
import pytest
from config import FEATURE_COLUMNS, TARGET_COLUMN
from clean import clean


def test_clean_drops_nulls():
    """Cleaning drops rows with nulls."""
    n = 10
    df = pd.DataFrame(
        {c: [1.0] * n for c in FEATURE_COLUMNS},
        columns=FEATURE_COLUMNS,
    )
    df[TARGET_COLUMN] = range(n)
    df.loc[2, "f1"] = None
    out = clean(df)
    assert len(out) == n - 1
    assert out["f1"].notna().all()


def test_clean_requires_columns():
    """Cleaning raises when required columns are missing."""
    df = pd.DataFrame({"f1": [1.0], "f2": [1.0]})  # missing f3, f4, f5, T
    with pytest.raises(ValueError, match="Missing columns"):
        clean(df)
