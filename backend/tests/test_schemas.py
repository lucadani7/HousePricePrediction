from typing import Any
import pytest
from pydantic import ValidationError

from housepriceprediction.api.schemas import HouseFeatures
from housepriceprediction.features import FORM_FEATURES


def valid_house(**overrides: Any) -> dict[str, Any]:
    """Helper function returning a valid dictionary of 16 house features,
    allowing selective overrides for test cases.
    """
    house: dict[str, Any] = {
        "first_floor_sf": 1200,
        "second_floor_sf": 800,
        "total_bsmt_sf": 1000,
        "bsmt_fin_sf1": 600,
        "overall_quality": 7,
        "overall_condition": 5,
        "kitchen_quality": "Gd",
        "year_built": 2005,
        "year_remod_add": 2005,
        "neighborhood": "CollgCr",
        "ms_zoning": "RL",
        "lot_area": 9500,
        "garage_cars": 2,
        "full_bath": 2,
        "half_bath": 1,
        "fireplaces": 1,
    }
    house.update(overrides)
    return house


def test_house_features_valid() -> None:
    features = HouseFeatures(**valid_house())
    df = features.to_model_frame()
    assert list(df.columns) == list(FORM_FEATURES)


def test_invalid_zoning() -> None:
    with pytest.raises(ValidationError):
        HouseFeatures(**valid_house(ms_zoning="I"))


def test_invalid_neighborhood() -> None:
    with pytest.raises(ValidationError):
        HouseFeatures(**valid_house(neighborhood="Atlantis"))


def test_invalid_overall_quality() -> None:
    with pytest.raises(ValidationError):
        HouseFeatures(**valid_house(overall_quality=11))


def test_remod_year_before_built() -> None:
    with pytest.raises(ValidationError):
        HouseFeatures(**valid_house(year_built=2010, year_remod_add=2005))


def test_basement_fin_exceeds_total() -> None:
    with pytest.raises(ValidationError):
        HouseFeatures(**valid_house(total_bsmt_sf=500, bsmt_fin_sf1=600))


def test_square_footage_exceeds_limit() -> None:
    with pytest.raises(ValidationError):
        HouseFeatures(**valid_house(first_floor_sf=2500, second_floor_sf=2000))