import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Tao Dividends API"}


def test_get_tao_dividends_unauthorized(client):
    response = client.get(
        "/api/v1/tao_dividends", params={"netuid": 1, "hotkey": "test"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_tao_dividends_authorized(client, test_token):
    response = client.get(
        "/api/v1/tao_dividends",
        params={"netuid": 1, "hotkey": "test"},
        headers={"Authorization": f"Bearer {test_token}"},
    )
    assert response.status_code == 200
    # TODO: Add more assertions once the endpoint is fully implemented
