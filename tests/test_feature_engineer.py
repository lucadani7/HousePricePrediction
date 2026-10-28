import numpy as np
import pandas as pd
import pytest

from housepriceprediction.features import DERIVED_COLUMNS
from housepriceprediction.transformers import FeatureEngineer


def test_feature_engineer_transforms_correctly():
    df = pd.DataFrame({
        "PoolArea": [500, 0, np.nan],
        "MSSubClass": [60, 20.0, 20.7],
        "MoSold": [5, 12, 3],
        "LotArea": [8450, 9600, 11250]
    })

    engineer = FeatureEngineer(add_derived=False)
    transformed = engineer.fit_transform(df)

    # Check Pool transformation
    assert "PoolArea" not in transformed.columns
    assert "HasPool" in transformed.columns
    assert list(transformed["HasPool"]) == [1, 0, 0]

    # Check safe string conversion
    assert transformed.loc[0, "MSSubClass"] == "60"
    assert transformed.loc[1, "MSSubClass"] == "20"
    assert transformed.loc[2, "MSSubClass"] == "20.7"
    assert transformed.loc[0, "MoSold"] == "5"

    # Check un-transformed columns remain untouched
    assert "LotArea" in transformed.columns
    pd.testing.assert_series_equal(transformed["LotArea"], df["LotArea"])


def test_feature_engineer_fail_fast_missing_columns():
    df = pd.DataFrame({"LotArea": [8450]})
    engineer = FeatureEngineer(add_derived=False)
    engineer.fit(df)

    with pytest.raises(KeyError):
        engineer.transform(df)


def test_feature_engineer_does_not_modify_original():
    df = pd.DataFrame({
        "PoolArea": [100],
        "MSSubClass": [60],
        "MoSold": [5]
    })
    original_copy = df.copy()

    engineer = FeatureEngineer(add_derived=False)
    engineer.transform(df)

    pd.testing.assert_frame_equal(df, original_copy)



@pytest.fixture
def sample_derived_data():
    return pd.DataFrame({
        "PoolArea": [0, 500],
        "MSSubClass": [60, 20],
        "MoSold": [5, 6],
        "TotalBsmtSF": [1000, np.nan],
        "1stFlrSF": [1000, 1200],
        "2ndFlrSF": [500, 0],
        "FullBath": [2, 1],
        "HalfBath": [1, 0],
        "BsmtFullBath": [1, 0],
        "BsmtHalfBath": [0, 1],
        "WoodDeckSF": [100, 0],
        "OpenPorchSF": [50, 0],
        "EnclosedPorch": [0, 20],
        "3SsnPorch": [0, 0],
        "ScreenPorch": [0, 0]
    })


def test_feature_engineer_add_derived_true(sample_derived_data):
    transformer = FeatureEngineer(add_derived=True)
    out = transformer.fit_transform(sample_derived_data)

    # Check existence
    for col in DERIVED_COLUMNS:
        assert col in out.columns, f"{col} is missing"

    # Check math for the first row (complete data)
    assert out["TotalSF"].iloc[0] == 2500.0
    assert out["TotalBath"].iloc[0] == 3.5
    assert out["TotalPorchSF"].iloc[0] == 150.0

    # Original components must be retained
    assert "TotalBsmtSF" in out.columns


def test_feature_engineer_add_derived_false(sample_derived_data):
    transformer = FeatureEngineer(add_derived=False)
    out = transformer.fit_transform(sample_derived_data)

    # Check they do not exist
    assert "TotalSF" not in out.columns
    assert "TotalBath" not in out.columns
    assert "TotalPorchSF" not in out.columns


def test_feature_engineer_nan_propagation(sample_derived_data):
    transformer = FeatureEngineer(add_derived=True)
    out = transformer.fit_transform(sample_derived_data)

    # The second row has NaN in TotalBsmtSF, so TotalSF must become NaN
    assert pd.isna(out["TotalSF"].iloc[1])
    # TotalBath should still calculate correctly
    assert out["TotalBath"].iloc[1] == 1.5


def test_feature_engineer_derived_missing_columns_fail_fast():
    # Only base columns exist, missing derived components
    df_missing = pd.DataFrame({
        "PoolArea": [0], "MSSubClass": [60], "MoSold": [5],
    })

    # Should fail fast when add_derived=True
    transformer_true = FeatureEngineer(add_derived=True)
    with pytest.raises(KeyError, match="Missing required columns"):
        transformer_true.fit_transform(df_missing)

    # Should pass when add_derived=False
    transformer_false = FeatureEngineer(add_derived=False)
    out = transformer_false.fit_transform(df_missing)
    assert "HasPool" in out.columns
