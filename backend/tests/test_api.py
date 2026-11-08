from fastapi.testclient import TestClient
from housepriceprediction.api.main import app


def test_health_check() -> None:
    """Checks health check route and teh fact the model is correctly loaded."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_predict_endpoint_success() -> None:
    """Checks that POST request is valid to /predict returns 200 status and a price."""
    payload = {
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

    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "predicted_price" in data
        assert isinstance(data["predicted_price"], float)
        assert data["predicted_price"] > 0


def test_predict_endpoint_validation_error() -> None:
    """Checks that invalid data sent to /predict are refused with 422 code."""
    payload = {
        "first_floor_sf": 1200,
        "second_floor_sf": 800,
        "total_bsmt_sf": 1000,
        "bsmt_fin_sf1": 600,
        "overall_quality": 15,  # Invalid: max is 10
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

    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        assert response.status_code == 422