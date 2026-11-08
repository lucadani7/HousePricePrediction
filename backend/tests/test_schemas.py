from typing import Any, Callable

import pytest
from pydantic import ValidationError

from housepriceprediction.api.schemas import HouseFeatures
from housepriceprediction.features import FORM_FEATURES

HouseFactory = Callable[..., dict[str, Any]]


def test_house_features_valid(valid_house: HouseFactory) -> None:
    features = HouseFeatures(**valid_house())
    df = features.to_model_frame()
    assert list(df.columns) == list(FORM_FEATURES)


def test_invalid_zoning(valid_house: HouseFactory) -> None:
    with pytest.raises(ValidationError):
        HouseFeatures(**valid_house(ms_zoning="I"))


def test_invalid_neighborhood(valid_house: HouseFactory) -> None:
    with pytest.raises(ValidationError):
        HouseFeatures(**valid_house(neighborhood="Atlantis"))


def test_invalid_overall_quality(valid_house: HouseFactory) -> None:
    with pytest.raises(ValidationError):
        HouseFeatures(**valid_house(overall_quality=11))


def test_remod_year_before_built(valid_house: HouseFactory) -> None:
    with pytest.raises(ValidationError):
        HouseFeatures(**valid_house(year_built=2010, year_remod_add=2005))


def test_basement_fin_exceeds_total(valid_house: HouseFactory) -> None:
    with pytest.raises(ValidationError):
        HouseFeatures(**valid_house(total_bsmt_sf=500, bsmt_fin_sf1=600))


def test_square_footage_exceeds_limit(valid_house: HouseFactory) -> None:
    with pytest.raises(ValidationError):
        HouseFeatures(**valid_house(first_floor_sf=2500, second_floor_sf=2000))
