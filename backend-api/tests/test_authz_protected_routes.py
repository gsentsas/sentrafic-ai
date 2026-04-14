def test_sites_requires_auth(client):
    response = client.get("/api/sites/")
    assert response.status_code == 401


def test_cameras_requires_auth(client):
    response = client.get("/api/cameras/")
    assert response.status_code == 401


def test_dashboard_requires_auth(client):
    response = client.get("/api/dashboard/overview")
    assert response.status_code == 401


def test_analytics_requires_auth(client):
    response = client.get("/api/analytics/traffic")
    assert response.status_code == 401


def test_alerts_requires_auth(client):
    response = client.get("/api/alerts/")
    assert response.status_code == 401


def test_exports_requires_auth(client):
    response = client.get("/api/exports/traffic.csv")
    assert response.status_code == 401
