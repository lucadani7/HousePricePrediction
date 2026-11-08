from typing import Any, Callable

import pytest
from fastapi.testclient import TestClient

from housepriceprediction.api.main import MODEL_PATH, app

HouseFactory = Callable[..., dict[str, Any]]

# The app loads model.joblib at startup: without it, skip instead of failing.
pytestmark = pytest.mark.skipif(
    not MODEL_PATH.exists(), reason="model.joblib not found. Run 'uv run train' first."
)


def test_health_check() -> None:
    """The health route answers and reports that the model is loaded."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_predict_endpoint_success(valid_house: HouseFactory) -> None:
    """A valid house returns 200 and a positive price."""
    with TestClient(app) as client:
        response = client.post("/predict", json=valid_house())
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["predicted_price"], float)
        assert data["predicted_price"] > 0


def test_predict_endpoint_field_validation_error(valid_house: HouseFactory) -> None:
    """A value outside a field's range is rejected with 422."""
    with TestClient(app) as client:
        response = client.post("/predict", json=valid_house(overall_quality=15))
        assert response.status_code == 422


def test_predict_endpoint_cross_field_validation_error(valid_house: HouseFactory) -> None:
    """A house that breaks a cross-field rule is rejected with 422."""
    with TestClient(app) as client:
        response = client.post("/predict", json=valid_house(year_built=2010, year_remod_add=2005))
        assert response.status_code == 422
