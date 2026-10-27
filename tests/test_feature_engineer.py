import numpy as np
import pandas as pd
import pytest
from housepriceprediction.transformers import FeatureEngineer


def test_feature_engineer_transforms_correctly():
    df = pd.DataFrame({
        "PoolArea": [500, 0, np.nan],
        "MSSubClass": [60, 20.0, 20.7],
        "MoSold": [5, 12, 3],
        "LotArea": [8450, 9600, 11250]
    })

    engineer = FeatureEngineer()
    transformed = engineer.fit_transform(df)

    # Check Pool transformation
    assert "PoolArea" not in transformed.columns
    assert "HasPool" in transformed.columns
    assert list(transformed["HasPool"]) == [1, 0, 0]

    # Check safe string conversion (no '.0', integer float converted, non-integer preserved)
    assert transformed.loc[0, "MSSubClass"] == "60"
    assert transformed.loc[1, "MSSubClass"] == "20"
    assert transformed.loc[2, "MSSubClass"] == "20.7"
    assert transformed.loc[0, "MoSold"] == "5"

    # Check un-transformed columns remain untouched
    assert "LotArea" in transformed.columns
    pd.testing.assert_series_equal(transformed["LotArea"], df["LotArea"])


def test_feature_engineer_fail_fast_missing_columns():
    df = pd.DataFrame({"LotArea": [8450]})
    engineer = FeatureEngineer()
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

    engineer = FeatureEngineer()
    engineer.transform(df)

    pd.testing.assert_frame_equal(df, original_copy)