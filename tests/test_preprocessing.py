import numpy as np
import pandas as pd
import pytest

from housepriceprediction.preprocessing import make_functional_pipeline


def test_functional_pipeline_transforms_correctly():
    # Input data containing a valid value, a missing value (NaN), and other valid categories
    df = pd.DataFrame({"Functional": ["Typ", np.nan, "Sal", "Min1"]})

    pipeline = make_functional_pipeline()
    transformed = pipeline.fit_transform(df)

    # Scale: ("Sal", "Sev", "Maj2", "Maj1", "Mod", "Min2", "Min1", "Typ")
    # - "Typ" -> index 7
    # - np.nan -> filled with constant "Typ" -> index 7
    # - "Sal" -> index 0
    # - "Min1" -> index 6
    expected = np.array([[7.0], [7.0], [0.0], [6.0]])
    np.testing.assert_array_equal(transformed, expected)


def test_functional_pipeline_fail_fast_unknown_value():
    # Fit the pipeline with valid categories
    df_train = pd.DataFrame({"Functional": ["Typ", "Min1"]})
    pipeline = make_functional_pipeline()
    pipeline.fit(df_train)

    # Transforming an invalid/unknown category ("Typical" instead of "Typ") must raise a ValueError
    df_invalid = pd.DataFrame({"Functional": ["Typical"]})

    with pytest.raises(ValueError):
        pipeline.transform(df_invalid)
