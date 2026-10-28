import numpy as np
import pandas as pd
import pytest

from housepriceprediction.config import DATA_RAW
from housepriceprediction.features import DERIVED_COLUMNS
from housepriceprediction.preprocessing import build_preprocessor, make_functional_pipeline


def test_functional_pipeline_transforms_correctly():
    df = pd.DataFrame({"Functional": ["Typ", np.nan, "Sal", "Min1"]})
    pipeline = make_functional_pipeline()
    transformed = pipeline.fit_transform(df)

    expected = np.array([[7.0], [7.0], [0.0], [6.0]])
    np.testing.assert_array_equal(transformed, expected)


def test_functional_pipeline_fail_fast_unknown_value():
    df_train = pd.DataFrame({"Functional": ["Typ", "Min1"]})
    pipeline = make_functional_pipeline()
    pipeline.fit(df_train)

    df_invalid = pd.DataFrame({"Functional": ["Typical"]})
    with pytest.raises(ValueError):
        pipeline.transform(df_invalid)


@pytest.mark.skipif(not (DATA_RAW / "train.csv").exists(), reason="Raw data not available")
def test_build_preprocessor_integration():
    train_df = pd.read_csv(DATA_RAW / "train.csv", keep_default_na=False, na_values=["NA"])
    test_df = pd.read_csv(DATA_RAW / "test.csv", keep_default_na=False, na_values=["NA"])

    X_train = train_df.drop(columns=["Id", "SalePrice"])
    X_test = test_df.drop(columns=["Id"])

    preprocessor = build_preprocessor()

    # Fit on train, transform both
    preprocessor.fit(X_train)
    X_train_trans = preprocessor.transform(X_train)
    X_test_trans = preprocessor.transform(X_test)

    # 1. Row counts must match input
    assert X_train_trans.shape[0] == X_train.shape[0]
    assert X_test_trans.shape[0] == X_test.shape[0]

    # 2. No missing values remaining
    assert not X_train_trans.isna().any().any()
    assert not X_test_trans.isna().any().any()

    # 3. All output columns must be numeric
    assert all(pd.api.types.is_numeric_dtype(dt) for dt in X_train_trans.dtypes)
    assert all(pd.api.types.is_numeric_dtype(dt) for dt in X_test_trans.dtypes)

    # 4. Train and test must produce exactly the same columns, in the same order
    assert list(X_train_trans.columns) == list(X_test_trans.columns)


@pytest.mark.skipif(not (DATA_RAW / "train.csv").exists(), reason="Raw data not available")
def test_build_preprocessor_add_derived_toggle():
    train_df = pd.read_csv(DATA_RAW / "train.csv", keep_default_na=False, na_values=["NA"])
    X_train = train_df.drop(columns=["Id", "SalePrice"])

    # Test True
    prep_true = build_preprocessor(add_derived=True)
    X_trans_true = prep_true.fit_transform(X_train)

    for col in DERIVED_COLUMNS:
        assert col in X_trans_true.columns, f"{col} was dropped silently by ColumnTransformer!"

    # Test False
    prep_false = build_preprocessor(add_derived=False)
    X_trans_false = prep_false.fit_transform(X_train)

    for col in DERIVED_COLUMNS:
        assert col not in X_trans_false.columns, f"{col} is present in output when add_derived=False"
