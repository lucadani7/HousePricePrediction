from collections.abc import Generator
from typing import Any, Callable

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from housepriceprediction.api.database import get_session
from housepriceprediction.api.main import MODEL_PATH, app


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


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """TestClient for the API, backed by an empty in-memory database.

    Requests made in tests never touch data/predictions.db. Skips the test when
    the trained model is missing, because the app loads it at startup.
    """
    if not MODEL_PATH.exists():
        pytest.skip("model.joblib not found. Run 'uv run train' first.")

    test_engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(test_engine)

    def override_get_session() -> Generator[Session, None, None]:
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # Runs even when the test fails, so the override never leaks into other tests.
        app.dependency_overrides.clear()
