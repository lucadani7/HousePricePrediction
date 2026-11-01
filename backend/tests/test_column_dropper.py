import pandas as pd
import pytest
from housepriceprediction.transformers import ColumnDropper
from housepriceprediction.transformers.column_dropper import DEFAULT_DROP_COLS


def test_column_dropper_drops_specified_columns():
    df = pd.DataFrame({
        "GarageYrBlt": [2003.0, 1976.0],
        "Street": ["Pave", "Pave"],
        "LotArea": [8450, 9600],
        "SalePrice": [208500, 181500]
    })

    dropper = ColumnDropper(columns=["GarageYrBlt", "Street"])
    transformed = dropper.fit_transform(df)

    assert "GarageYrBlt" not in transformed.columns
    assert "Street" not in transformed.columns

    expected = pd.DataFrame({
        "LotArea": [8450, 9600],
        "SalePrice": [208500, 181500]
    })
    pd.testing.assert_frame_equal(transformed, expected)


def test_column_dropper_uses_defaults():
    df = pd.DataFrame({
        "GarageYrBlt": [2003.0],
        "Street": ["Pave"],
        "Utilities": ["AllPub"],
        "Condition2": ["Norm"],
        "RoofMatl": ["CompShg"],
        "Heating": ["GasA"],
        "PoolQC": ["Ex"],
        "LotArea": [8450]
    })

    dropper = ColumnDropper()
    transformed = dropper.fit_transform(df)

    for col in DEFAULT_DROP_COLS:
        assert col not in transformed.columns

    assert "LotArea" in transformed.columns


def test_column_dropper_fail_fast_missing_column():
    df = pd.DataFrame({
        "LotArea": [8450]
    })

    dropper = ColumnDropper(columns=["NonExistentCol"])
    dropper.fit(df)

    with pytest.raises(KeyError):
        dropper.transform(df)


def test_column_dropper_does_not_modify_original():
    df = pd.DataFrame({
        "GarageYrBlt": [2003.0],
        "LotArea": [8450]
    })
    original_copy = df.copy()

    dropper = ColumnDropper(columns=["GarageYrBlt"])
    dropper.transform(df)

    pd.testing.assert_frame_equal(df, original_copy)
