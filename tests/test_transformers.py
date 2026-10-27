import numpy as np
import pandas as pd
import pytest
from sklearn.exceptions import NotFittedError
from housepriceprediction.transformers.neighborhood_median import NeighborhoodMedianImputer


def test_neighborhood_median_imputer_basic():
    train_df = pd.DataFrame({
        "Neighborhood": ["CollgCr", "CollgCr", "Veenker", "Veenker"],
        "LotFrontage": [70.0, 80.0, 60.0, 60.0]
    })

    imputer = NeighborhoodMedianImputer()
    imputer.fit(train_df)

    # Test data with missing values and one existing value to verify it's preserved
    test_df = pd.DataFrame({
        "Neighborhood": ["CollgCr", "Vveenker", "CollgCr"],
        "LotFrontage": [np.nan, np.nan, 90.0]
    })

    transformed = imputer.transform(test_df)

    assert transformed.loc[0, "LotFrontage"] == 75.0  # CollgCr median
    assert transformed.loc[1, "LotFrontage"] == 65.0  # Unseen hood falls back to global median
    assert transformed.loc[2, "LotFrontage"] == 90.0  # Existing value is preserved untouched


def test_neighborhood_imputer_all_nan_group():
    train_df = pd.DataFrame({
        "Neighborhood": ["CollgCr", "CollgCr", "EmptyHood", "EmptyHood"],
        "LotFrontage": [70.0, 80.0, np.nan, np.nan]
    })

    imputer = NeighborhoodMedianImputer()
    imputer.fit(train_df)

    test_df = pd.DataFrame({
        "Neighborhood": ["EmptyHood"],
        "LotFrontage": [np.nan]
    })

    transformed = imputer.transform(test_df)
    assert transformed.loc[0, "LotFrontage"] == 75.0


def test_transformer_does_not_modify_original():
    train_df = pd.DataFrame({
        "Neighborhood": ["CollgCr", "CollgCr"],
        "LotFrontage": [70.0, np.nan]
    })
    imputer = NeighborhoodMedianImputer()
    imputer.fit(train_df)

    original_copy = train_df.copy()
    imputer.transform(train_df)

    pd.testing.assert_frame_equal(train_df, original_copy)


def test_fail_fast_missing_columns():
    train_df = pd.DataFrame({
        "Neighborhood": ["CollgCr"],
        "LotFrontage": [70.0]
    })
    imputer = NeighborhoodMedianImputer().fit(train_df)

    # Missing LotFrontage
    bad_df = pd.DataFrame({"Neighborhood": ["CollgCr"]})
    with pytest.raises(KeyError):
        imputer.transform(bad_df)


def test_not_fitted_error():
    imputer = NeighborhoodMedianImputer()
    test_df = pd.DataFrame({
        "Neighborhood": ["CollgCr"],
        "LotFrontage": [np.nan]
    })
    with pytest.raises(NotFittedError):
        imputer.transform(test_df)
