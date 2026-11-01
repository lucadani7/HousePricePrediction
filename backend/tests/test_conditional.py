import numpy as np
import pandas as pd
import pytest
from housepriceprediction.config import DATA_RAW
from housepriceprediction.transformers.conditional import ConditionalGroup, ConditionalImputer


GARAGE_GROUP = ConditionalGroup(
    parent_col="GarageType",
    is_numeric_parent=False,
    numeric_cols=("GarageArea",),
    categorical_cols=("GarageFinish",),
)

MASONRY_GROUP = ConditionalGroup(
    parent_col="MasVnrArea",
    is_numeric_parent=True,
    numeric_cols=("MasVnrArea",),
    categorical_cols=("MasVnrType",),
)

BASEMENT_GROUP = ConditionalGroup(
    parent_col="TotalBsmtSF",
    is_numeric_parent=True,
    numeric_cols=("BsmtFinSF1",),
    categorical_cols=("BsmtQual",),
)

def test_conditional_imputer_pure_none():
    train_df = pd.DataFrame({
        "Alley": [np.nan, "Pave"],
        "Fence": [np.nan, np.nan],
        "MiscFeature": [np.nan, np.nan]
    })
    imputer = ConditionalImputer(pure_none_cols=["Alley"], conditional_groups=[])
    imputer.fit(train_df)

    test_df = pd.DataFrame({
        "Alley": [np.nan]
    })
    transformed = imputer.transform(test_df)
    assert transformed.loc[0, "Alley"] == "None"


def test_conditional_imputer_garage_existing_missing_details():
    # Training: Garage exists ('Detchd'), Area=500, Finish='Unf'
    train_df = pd.DataFrame({
        "GarageType": ["Detchd", "None"],
        "GarageArea": [500.0, 0.0],
        "GarageFinish": ["Unf", "None"]
    })

    imputer = ConditionalImputer(pure_none_cols=[], conditional_groups=[GARAGE_GROUP])
    imputer.fit(train_df)

    # Test: Garage exists ('Detchd'), but Area and Finish are NaN
    test_df = pd.DataFrame({
        "GarageType": ["Detchd"],
        "GarageArea": [np.nan],
        "GarageFinish": [np.nan]
    })

    transformed = imputer.transform(test_df)
    assert transformed.loc[0, "GarageArea"] == 500.0
    assert transformed.loc[0, "GarageFinish"] == "Unf"


def test_conditional_imputer_masonry_and_existing_values():
    # Training: MasVnrArea=198.0, MasVnrType='BrkFace'
    train_df = pd.DataFrame({
        "MasVnrArea": [198.0, 0.0],
        "MasVnrType": ["BrkFace", "None"]
    })

    imputer = ConditionalImputer(pure_none_cols=[], conditional_groups=[MASONRY_GROUP])
    imputer.fit(train_df)

    # Test: Area is 198.0 (exists), Type is missing. Also test that existing valid values are untouched.
    test_df = pd.DataFrame({
        "MasVnrArea": [198.0, 50.0],
        "MasVnrType": [np.nan, "Stone"]
    })

    transformed = imputer.transform(test_df)
    assert transformed.loc[0, "MasVnrType"] == "BrkFace"
    assert transformed.loc[1, "MasVnrType"] == "Stone"  # untouched


def test_conditional_imputer_fail_fast_missing_columns():
    train_df = pd.DataFrame({
        "TotalBsmtSF": [800.0],
        "BsmtFinSF1": [400.0],
        "BsmtQual": ["TA"]
    })
    imputer = ConditionalImputer(pure_none_cols=[], conditional_groups=[BASEMENT_GROUP]).fit(train_df)

    bad_df = pd.DataFrame({"TotalBsmtSF": [100.0]})  # Missing BsmtFinSF1 and BsmtQual
    with pytest.raises(KeyError):
        imputer.transform(bad_df)


def test_conditional_imputer_parent_filled():
    train_df = pd.DataFrame({
        "GarageType": ["Attchd", "None"],
        "GarageArea": [600.0, 0.0],
        "GarageFinish": ["Fin", "None"]
    })
    imputer = ConditionalImputer(pure_none_cols=[], conditional_groups=[GARAGE_GROUP])
    imputer.fit(train_df)

    test_df = pd.DataFrame({
        "GarageType": [np.nan],
        "GarageArea": [np.nan],
        "GarageFinish": [np.nan]
    })
    transformed = imputer.transform(test_df)
    assert transformed.loc[0, "GarageType"] == "None"


@pytest.mark.skipif(not (DATA_RAW / "train.csv").exists(), reason="Raw data not available")
def test_conditional_imputer_on_real_data():
    train_df = pd.read_csv(DATA_RAW / "train.csv", keep_default_na=False, na_values=["NA"])
    test_df = pd.read_csv(DATA_RAW / "test.csv", keep_default_na=False, na_values=["NA"])

    imputer = ConditionalImputer()
    imputer.fit(train_df)
    transformed_test = imputer.transform(test_df)

    # 1. Strict assertions on specific houses
    house_2121 = transformed_test[transformed_test["Id"] == 2121]
    assert len(house_2121) == 1
    assert house_2121["BsmtQual"].values[0] == "None"

    house_2577 = transformed_test[transformed_test["Id"] == 2577]
    assert len(house_2577) == 1
    assert house_2577["GarageType"].values[0] == "Detchd"
    assert house_2577["GarageFinish"].values[0] != "None"
    assert house_2577["GarageCars"].values[0] > 0  # type: ignore[operator]
    assert house_2577["GarageArea"].values[0] > 0  # type: ignore[operator]


    house_2611 = transformed_test[transformed_test["Id"] == 2611]
    assert len(house_2611) == 1
    assert house_2611["MasVnrArea"].values[0] > 0 # type: ignore[operator]
    assert house_2611["MasVnrType"].values[0] != "None"

    # 2. Global invariant: no NaNs should remain in any managed column
    pure_cols = imputer._get_pure_none_cols()
    groups = imputer._get_conditional_groups()

    managed_cols = list(pure_cols)
    for g in groups:
        managed_cols.append(g.parent_col)
        managed_cols.extend(g.numeric_cols)
        managed_cols.extend(g.categorical_cols)

    for col in managed_cols:
        assert not transformed_test[col].isna().any(), f"Column {col} still contains missing values!"


def test_conditional_imputer_int_column_with_fractional_median():
    # Regression test: an int64 column with no missing values must not break
    # when the learned median has decimals (400 and 401 -> median 400.5).
    df = pd.DataFrame({
        "TotalBsmtSF": [800, 900],      # both houses have a basement
        "BsmtFinSF1": [400, 401],       # int64, no NaN, median = 400.5
        "BsmtQual": ["TA", "Gd"],
    })
    assert df["BsmtFinSF1"].dtype == "int64"   # make sure we reproduce the real situation

    imputer = ConditionalImputer(pure_none_cols=[], conditional_groups=[BASEMENT_GROUP])
    imputer.fit(df)
    transformed = imputer.transform(df)

    # Existing values must stay exactly the same
    assert list(transformed["BsmtFinSF1"]) == [400, 401]


