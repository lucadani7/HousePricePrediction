from pathlib import Path
import pandas as pd
import pytest

from housepriceprediction.features import (
    ORDINAL_CATEGORIES,
    NOMINAL_COLUMNS,
    NUMERIC_COLUMNS,
)
from housepriceprediction.transformers import (
    ColumnDropper,
    FeatureEngineer,
    NeighborhoodMedianImputer,
    ConditionalImputer,
)

DATA_RAW = Path("data/raw")


@pytest.mark.skipif(not (DATA_RAW / "train.csv").exists(), reason="Raw data not available")
def test_feature_groups_integrity():
    train_df = pd.read_csv(DATA_RAW / "train.csv", keep_default_na=False, na_values=["NA"])
    X = train_df.drop(columns=["Id", "SalePrice"])

    # Apply preprocessing steps 1-4
    X_trans = ColumnDropper().fit_transform(X)
    X_trans = FeatureEngineer().fit_transform(X_trans)
    X_trans = NeighborhoodMedianImputer().fit_transform(X_trans)
    X_trans = ConditionalImputer().fit_transform(X_trans)

    ordinal_cols = list(ORDINAL_CATEGORIES.keys())
    numeric_cols = list(NUMERIC_COLUMNS)
    nominal_cols = list(NOMINAL_COLUMNS)

    all_processed = set(X_trans.columns)
    all_grouped = set(ordinal_cols) | set(numeric_cols) | set(nominal_cols)

    # 1. Total coverage check
    assert all_processed == all_grouped, (
        f"Mismatch in columns!\n"
        f"Missing: {all_processed - all_grouped}\n"
        f"Extra: {all_grouped - all_processed}"
    )

    # 2. Uniqueness check (no overlaps between groups)
    assert not (set(numeric_cols) & set(ordinal_cols)), "Overlap between numeric and ordinal"
    assert not (set(nominal_cols) & set(ordinal_cols)), "Overlap between nominal and ordinal"
    assert not (set(numeric_cols) & set(nominal_cols)), "Overlap between numeric and nominal"
