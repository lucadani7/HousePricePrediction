import pandas as pd
import pytest
from sklearn.exceptions import NotFittedError

from housepriceprediction.transformers.form_input_masker import FormInputMasker


def test_form_input_masker_api_case():
    data = pd.DataFrame({
        "1stFlrSF": [1000, 1500],
        "2ndFlrSF": [500, 0],
        "TotalBsmtSF": [800, 1000],
        "BsmtFinSF1": [500, 600],
        "OverallQual": [7, 5],
        "OverallCond": [5, 5],
        "KitchenQual": ["Gd", "TA"],
        "YearBuilt": [2000, 1980],
        "YearRemodAdd": [2005, 1990],
        "Neighborhood": ["CollgCr", "OldTown"],
        "MSZoning": ["RL", "RM"],
        "LotArea": [9000, 8000],
        "GarageCars": [2, 1],
        "FullBath": [2, 1],
        "HalfBath": [1, 0],
        "Fireplaces": [1, 0],
        "ExtraColumn": [100, 200],
    })

    form_features = tuple(col for col in data.columns if col != "ExtraColumn")

    masker = FormInputMasker(form_features=form_features)
    masker.fit(data)

    api_input = data[list(form_features)].copy()

    transformed = masker.transform(api_input)

    assert list(transformed.columns) == list(data.columns)
    assert not transformed["ExtraColumn"].isna().any()
    assert (transformed["ExtraColumn"] == 150).all()


def test_form_input_masker_not_fitted_error():
    masker = FormInputMasker()
    data = pd.DataFrame({"1stFlrSF": [1000]})

    with pytest.raises(NotFittedError):
        masker.transform(data)


def test_form_input_masker_categorical_mode():
    data = pd.DataFrame({
        "1stFlrSF": [1000, 1500, 2000],
        "2ndFlrSF": [0, 0, 0],
        "TotalBsmtSF": [500, 500, 500],
        "BsmtFinSF1": [100, 100, 100],
        "OverallQual": [5, 5, 5],
        "OverallCond": [5, 5, 5],
        "KitchenQual": ["TA", "TA", "TA"],
        "YearBuilt": [1990, 1990, 1990],
        "YearRemodAdd": [1990, 1990, 1990],
        "Neighborhood": ["CollgCr", "CollgCr", "CollgCr"],
        "MSZoning": ["RL", "RL", "RL"],
        "LotArea": [8000, 8000, 8000],
        "GarageCars": [1, 1, 1],
        "FullBath": [1, 1, 1],
        "HalfBath": [0, 0, 0],
        "Fireplaces": [0, 0, 0],
        "ExtraCategorical": ["A", "A", "B"],
    })

    form_features = tuple(col for col in data.columns if col != "ExtraCategorical")

    masker = FormInputMasker(form_features=form_features)
    masker.fit(data)

    transformed = masker.transform(data[list(form_features)])
    assert (transformed["ExtraCategorical"] == "A").all()


def test_form_input_masker_does_not_modify_input():
    data = pd.DataFrame({
        "1stFlrSF": [1000],
        "2ndFlrSF": [500],
        "TotalBsmtSF": [800],
        "BsmtFinSF1": [500],
        "OverallQual": [7],
        "OverallCond": [5],
        "KitchenQual": ["Gd"],
        "YearBuilt": [2000],
        "YearRemodAdd": [2005],
        "Neighborhood": ["CollgCr"],
        "MSZoning": ["RL"],
        "LotArea": [9000],
        "GarageCars": [2],
        "FullBath": [2],
        "HalfBath": [1],
        "Fireplaces": [1],
        "ExtraNumeric": [999],
    })

    form_features = tuple(col for col in data.columns if col != "ExtraNumeric")
    masker = FormInputMasker(form_features=form_features)
    masker.fit(data)

    original_val = data["ExtraNumeric"].iloc[0]
    _ = masker.transform(data)

    assert data["ExtraNumeric"].iloc[0] == original_val


def test_form_input_masker_raises_key_error_after_fitting():
    data = pd.DataFrame({
        "1stFlrSF": [1000],
        "2ndFlrSF": [500],
        "TotalBsmtSF": [800],
        "BsmtFinSF1": [500],
        "OverallQual": [7],
        "OverallCond": [5],
        "KitchenQual": ["Gd"],
        "YearBuilt": [2000],
        "YearRemodAdd": [2005],
        "Neighborhood": ["CollgCr"],
        "MSZoning": ["RL"],
        "LotArea": [9000],
        "GarageCars": [2],
        "FullBath": [2],
        "HalfBath": [1],
        "Fireplaces": [1],
    })

    masker = FormInputMasker(form_features=tuple(data.columns))
    masker.fit(data)

    incomplete_data = data.drop(columns=["OverallQual"])

    with pytest.raises(KeyError):
        masker.transform(incomplete_data)