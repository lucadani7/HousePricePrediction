from typing import Any, Callable

import pytest


@pytest.fixture
def valid_house() -> Callable[..., dict[str, Any]]:
    """Returns a function that builds a valid web-form house (16 API fields).

    Pass keyword arguments to override single fields, e.g. valid_house(overall_quality=11).
    """

    def make(**overrides: Any) -> dict[str, Any]:
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

    return make
