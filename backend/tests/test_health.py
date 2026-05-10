from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_redis_connected():
    with patch("app.routers.health.ping_redis", new_callable=AsyncMock, return_value=True):
        response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["redis"] == "connected"
    assert "version" in data


def test_health_redis_unavailable():
    with patch("app.routers.health.ping_redis", new_callable=AsyncMock, return_value=False):
        response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["redis"] == "unavailable"
