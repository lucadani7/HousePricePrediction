from typing import Any, Callable

from fastapi.testclient import TestClient

HouseFactory = Callable[..., dict[str, Any]]


def test_health_check(client: TestClient) -> None:
    """The health route answers and reports that the model is loaded."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_endpoint_success(client: TestClient, valid_house: HouseFactory) -> None:
    """A valid house returns 200 and a positive price."""
    response = client.post("/predict", json=valid_house())
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["predicted_price"], float)
    assert data["predicted_price"] > 0


def test_predict_endpoint_field_validation_error(
    client: TestClient, valid_house: HouseFactory
) -> None:
    """A value outside a field's range is rejected with 422."""
    response = client.post("/predict", json=valid_house(overall_quality=15))
    assert response.status_code == 422


def test_predict_endpoint_cross_field_validation_error(
    client: TestClient, valid_house: HouseFactory
) -> None:
    """A house that breaks a cross-field rule is rejected with 422."""
    response = client.post("/predict", json=valid_house(year_built=2010, year_remod_add=2005))
    assert response.status_code == 422
