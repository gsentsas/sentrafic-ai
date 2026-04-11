import pytest
from app.models.site import Site, SiteType
from app.models.camera import Camera, CameraStatus
from app.models.traffic_aggregate import TrafficAggregate, CongestionLevel
from datetime import datetime, timezone


def test_dashboard_overview(client, db):
    """Test dashboard overview endpoint."""
    # Create test data
    site = Site(
        name="Dashboard Test Site",
        slug="dashboard-test-site",
        address="Dashboard Address",
        city="Dakar",
        latitude=14.7167,
        longitude=-17.4667,
        site_type=SiteType.intersection,
    )
    db.add(site)
    db.flush()

    camera = Camera(
        site_id=site.id,
        name="Dashboard Camera",
        stream_url="rtsp://dashboard.example.com",
        status=CameraStatus.online,
    )
    db.add(camera)
    db.commit()

    # Test dashboard endpoint
    response = client.get("/api/dashboard/overview")
    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "summary" in data
    assert "alerts" in data
    assert "timestamp" in data

    # Verify summary fields
    summary = data["summary"]
    assert "total_sites" in summary
    assert "total_cameras" in summary
    assert "cameras_online" in summary
    assert "cameras_offline" in summary
    assert "total_vehicles_today" in summary

    # Verify we have at least one site and camera
    assert summary["total_sites"] >= 1
    assert summary["total_cameras"] >= 1
    assert summary["cameras_online"] >= 1


def test_dashboard_with_traffic_data(client, db):
    """Test dashboard with traffic data."""
    # Create test data
    site = Site(
        name="Traffic Dashboard Site",
        slug="traffic-dashboard-site",
        address="Traffic Address",
        city="Dakar",
        latitude=14.7167,
        longitude=-17.4667,
        site_type=SiteType.intersection,
    )
    db.add(site)
    db.flush()

    camera = Camera(
        site_id=site.id,
        name="Traffic Camera",
        stream_url="rtsp://traffic.example.com",
        status=CameraStatus.online,
    )
    db.add(camera)
    db.flush()

    # Add traffic aggregates for today
    now = datetime.now(timezone.utc)
    aggregate = TrafficAggregate(
        camera_id=camera.id,
        timestamp=now,
        period_seconds=300,
        car_count=100,
        bus_count=5,
        truck_count=2,
        motorcycle_count=20,
        person_count=15,
        total_count=142,
        avg_occupancy=0.71,
        congestion_level=CongestionLevel.moderate,
    )
    db.add(aggregate)
    db.commit()

    # Test dashboard endpoint
    response = client.get("/api/dashboard/overview")
    assert response.status_code == 200
    data = response.json()

    # Verify traffic data is reflected
    assert data["summary"]["total_vehicles_today"] > 0


def test_dashboard_with_alerts(client, db):
    """Test dashboard with alerts."""
    from app.models.alert import Alert, AlertType, AlertSeverity

    # Create test data
    site = Site(
        name="Alert Dashboard Site",
        slug="alert-dashboard-site",
        address="Alert Address",
        city="Dakar",
        latitude=14.7167,
        longitude=-17.4667,
        site_type=SiteType.intersection,
    )
    db.add(site)
    db.flush()

    camera = Camera(
        site_id=site.id,
        name="Alert Camera",
        stream_url="rtsp://alert.example.com",
        status=CameraStatus.online,
    )
    db.add(camera)
    db.flush()

    # Add unresolved alerts
    alert = Alert(
        camera_id=camera.id,
        site_id=site.id,
        alert_type=AlertType.congestion,
        severity=AlertSeverity.critical,
        message="High traffic congestion",
        is_resolved=False,
    )
    db.add(alert)
    db.commit()

    # Test dashboard endpoint
    response = client.get("/api/dashboard/overview")
    assert response.status_code == 200
    data = response.json()

    # Verify alerts are shown
    assert data["alerts"]["unresolved"] >= 1
    assert len(data["alerts"]["recent"]) > 0
