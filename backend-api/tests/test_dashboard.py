import pytest
from datetime import datetime, timezone

from app.models.site import Site, SiteType
from app.models.camera import Camera, CameraStatus
from app.models.traffic_aggregate import TrafficAggregate, CongestionLevel
from app.models.alert import Alert, AlertType, AlertSeverity


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _make_site(db, slug="dash-site"):
    site = Site(
        name="Dashboard Test Site", slug=slug,
        address="123 Test Address", city="Dakar",
        latitude=14.7167, longitude=-17.4667,
        site_type=SiteType.intersection,
    )
    db.add(site)
    db.flush()
    return site


def _make_camera(db, site_id, status=CameraStatus.online):
    cam = Camera(
        site_id=site_id, name="Dashboard Camera",
        stream_url="rtsp://dashboard.example.com",
        status=status,
    )
    db.add(cam)
    db.flush()
    return cam


# ──────────────────────────────────────────────────────────────────────────────
# Dashboard overview
# ──────────────────────────────────────────────────────────────────────────────

def test_dashboard_overview_structure(admin_client, db):
    """L'overview renvoie la structure attendue."""
    response = admin_client.get("/api/dashboard/overview")
    assert response.status_code == 200
    data = response.json()

    # Vérifier les clés principales
    assert "summary" in data
    assert "congestion" in data
    assert "recent_alerts" in data
    assert "traffic_trend_24h" in data
    assert "watchlist" in data
    assert "timestamp" in data

    # Vérifier les champs du summary
    summary = data["summary"]
    for field in (
        "total_sites", "total_cameras", "cameras_online", "cameras_offline",
        "online_percentage", "total_vehicles_today", "alerts_unresolved", "alerts_critical",
    ):
        assert field in summary, f"Champ manquant : {field}"


def test_dashboard_overview_counts(admin_client, db):
    """L'overview reflète les objets créés en base."""
    site = _make_site(db)
    cam = _make_camera(db, site.id, CameraStatus.online)
    db.commit()

    response = admin_client.get("/api/dashboard/overview")
    assert response.status_code == 200
    data = response.json()

    assert data["summary"]["total_sites"] >= 1
    assert data["summary"]["total_cameras"] >= 1
    assert data["summary"]["cameras_online"] >= 1


def test_dashboard_reflects_traffic_data(admin_client, db):
    """Les véhicules du jour sont comptabilisés."""
    site = _make_site(db, "traffic-dash-site")
    cam = _make_camera(db, site.id)
    agg = TrafficAggregate(
        camera_id=cam.id,
        timestamp=datetime.now(timezone.utc),
        period_seconds=300,
        car_count=100, bus_count=5, truck_count=2,
        motorcycle_count=20, person_count=15,
        total_count=142,
        avg_occupancy=0.71,
        congestion_level=CongestionLevel.moderate,
    )
    db.add(agg)
    db.commit()

    response = admin_client.get("/api/dashboard/overview")
    assert response.status_code == 200
    assert response.json()["summary"]["total_vehicles_today"] >= 142


def test_dashboard_reflects_unresolved_alerts(admin_client, db):
    """Les alertes non résolues sont comptabilisées dans le summary."""
    site = _make_site(db, "alert-dash-site")
    cam = _make_camera(db, site.id)
    alert = Alert(
        camera_id=cam.id, site_id=site.id,
        alert_type=AlertType.congestion,
        severity=AlertSeverity.critical,
        message="Congestion test",
        is_resolved=False,
    )
    db.add(alert)
    db.commit()

    response = admin_client.get("/api/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["alerts_unresolved"] >= 1
    assert data["summary"]["alerts_critical"] >= 1


def test_dashboard_live_summary(admin_client, db):
    """Le live-summary renvoie les caméras actives avec last_reading."""
    site = _make_site(db, "live-summary-site")
    cam = _make_camera(db, site.id, CameraStatus.online)
    db.add(
        TrafficAggregate(
            camera_id=cam.id,
            timestamp=datetime.now(timezone.utc),
            period_seconds=300,
            car_count=8, bus_count=1, truck_count=1,
            motorcycle_count=3, person_count=2,
            total_count=15,
            avg_occupancy=0.42,
            congestion_level=CongestionLevel.moderate,
        )
    )
    db.commit()

    response = admin_client.get("/api/dashboard/live-summary")
    assert response.status_code == 200
    data = response.json()
    assert "cameras" in data
    assert isinstance(data["cameras"], list)
    target = next((c for c in data["cameras"] if c["camera_id"] == str(cam.id)), None)
    assert target is not None
    assert target["last_reading"] is not None
    assert "is_stale" in target["last_reading"]


def test_dashboard_live_summary_filters(admin_client, db):
    """Le live-summary supporte les filtres site_id et status."""
    site_a = _make_site(db, "live-summary-filter-a")
    site_b = _make_site(db, "live-summary-filter-b")
    cam_a = _make_camera(db, site_a.id, CameraStatus.online)
    _make_camera(db, site_b.id, CameraStatus.error)
    db.commit()

    response = admin_client.get(
        f"/api/dashboard/live-summary?site_id={site_a.id}&status=online"
    )
    assert response.status_code == 200
    cameras = response.json()["cameras"]
    assert len(cameras) == 1
    assert cameras[0]["camera_id"] == str(cam_a.id)


# ──────────────────────────────────────────────────────────────────────────────
# Analytics
# ──────────────────────────────────────────────────────────────────────────────

def test_analytics_traffic_date_format(admin_client, db):
    """Accepte le format YYYY-MM-DD pour start_date / end_date."""
    response = admin_client.get(
        "/api/analytics/traffic"
        "?start_date=2026-04-01&end_date=2026-04-14&granularity=hour"
    )
    assert response.status_code == 200


def test_analytics_distribution(admin_client, db):
    """L'endpoint de distribution retourne la structure attendue."""
    response = admin_client.get("/api/analytics/distribution?period_hours=24")
    assert response.status_code == 200
    data = response.json()
    assert "distribution" in data
    assert "total_count" in data


# ──────────────────────────────────────────────────────────────────────────────
# Alertes — résolution
# ──────────────────────────────────────────────────────────────────────────────

def test_resolve_alert(admin_client, db):
    """Résoudre une alerte met is_resolved = True."""
    site = _make_site(db, "resolve-site")
    cam = _make_camera(db, site.id)
    alert = Alert(
        camera_id=cam.id, site_id=site.id,
        alert_type=AlertType.congestion,
        severity=AlertSeverity.warning,
        message="Test congestion",
        is_resolved=False,
    )
    db.add(alert)
    db.commit()

    response = admin_client.post(f"/api/alerts/{alert.id}/resolve", json={})
    assert response.status_code == 200

    db.refresh(alert)
    assert alert.is_resolved is True
    assert alert.resolved_at is not None
