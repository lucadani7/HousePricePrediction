from typing import Any, Callable

from fastapi.testclient import TestClient

HouseFactory = Callable[..., dict[str, Any]]


def test_predict_saves_to_database(client: TestClient, valid_house: HouseFactory) -> None:
    """A successful prediction is stored and returned by /predictions."""
    response = client.post("/predict", json=valid_house())
    assert response.status_code == 200

    history = client.get("/predictions").json()
    assert len(history) == 1
    assert history[0]["predicted_price"] == response.json()["predicted_price"]
    assert history[0]["features"]["first_floor_sf"] == 1200


def test_rejected_request_is_not_saved(client: TestClient, valid_house: HouseFactory) -> None:
    """A request rejected by validation (422) leaves the history empty."""
    response = client.post("/predict", json=valid_house(overall_quality=15))
    assert response.status_code == 422
    assert client.get("/predictions").json() == []


def test_predictions_newest_first_and_limited(
    client: TestClient, valid_house: HouseFactory
) -> None:
    """History is ordered newest first and respects the limit parameter."""
    for area in (1000, 1100, 1200):
        client.post("/predict", json=valid_house(first_floor_sf=area))

    history = client.get("/predictions", params={"limit": 2}).json()
    assert [item["features"]["first_floor_sf"] for item in history] == [1200, 1100]


def test_predictions_limit_out_of_range(client: TestClient) -> None:
    """limit outside 1..100 is rejected with 422."""
    assert client.get("/predictions", params={"limit": 0}).status_code == 422
    assert client.get("/predictions", params={"limit": 101}).status_code == 422
