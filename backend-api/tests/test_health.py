import pytest


def test_root_health_check(client):
    """Test root health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "SEN TRAFIC AI"


def test_api_health_check(client):
    """Test API health check endpoint."""
    response = client.get("/api/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "services" in response.json()


def test_api_health_cameras(client, db):
    """Test API health cameras endpoint."""
    response = client.get("/api/health/cameras")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "online" in data
    assert "offline" in data
