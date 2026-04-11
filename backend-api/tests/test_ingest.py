import pytest
from datetime import datetime, timezone
import uuid

from app.models.site import Site, SiteType
from app.models.camera import Camera, CameraStatus


def test_ingest_valid_event(client, db):
    """Test ingesting valid traffic events."""
    # Create test site and camera
    site = Site(
        name="Ingest Test Site",
        slug="ingest-test-site",
        address="Ingest Test Address",
        city="Dakar",
        latitude=14.7167,
        longitude=-17.4667,
        site_type=SiteType.intersection,
    )
    db.add(site)
    db.flush()

    camera = Camera(
        site_id=site.id,
        name="Ingest Test Camera",
        stream_url="rtsp://test.example.com",
        status=CameraStatus.offline,
    )
    db.add(camera)
    db.commit()

    # Test ingest endpoint
    response = client.post(
        "/api/ingest/events",
        json={
            "events": [
                {
                    "camera_id": str(camera.id),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "period_seconds": 300,
                    "counts": {
                        "car": 45,
                        "bus": 3,
                        "truck": 2,
                        "motorcycle": 8,
                        "person": 12,
                    },
                    "avg_occupancy": 0.65,
                    "congestion_level": "moderate",
                }
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["received_count"] == 1
    assert data["processed_count"] == 1
    assert data["status"] == "success"


def test_ingest_multiple_events(client, db):
    """Test ingesting multiple traffic events."""
    # Create test site and cameras
    site = Site(
        name="Multi Ingest Site",
        slug="multi-ingest-site",
        address="Multi Address",
        city="Dakar",
        latitude=14.7167,
        longitude=-17.4667,
        site_type=SiteType.intersection,
    )
    db.add(site)
    db.flush()

    camera1 = Camera(
        site_id=site.id,
        name="Camera 1",
        stream_url="rtsp://camera1.example.com",
        status=CameraStatus.offline,
    )
    camera2 = Camera(
        site_id=site.id,
        name="Camera 2",
        stream_url="rtsp://camera2.example.com",
        status=CameraStatus.offline,
    )
    db.add(camera1)
    db.add(camera2)
    db.commit()

    # Test ingest with multiple events
    now = datetime.now(timezone.utc)
    response = client.post(
        "/api/ingest/events",
        json={
            "events": [
                {
                    "camera_id": str(camera1.id),
                    "timestamp": now.isoformat(),
                    "period_seconds": 300,
                    "counts": {"car": 50, "bus": 2, "truck": 1, "motorcycle": 10, "person": 5},
                    "avg_occupancy": 0.5,
                    "congestion_level": "free",
                },
                {
                    "camera_id": str(camera2.id),
                    "timestamp": now.isoformat(),
                    "period_seconds": 300,
                    "counts": {"car": 80, "bus": 5, "truck": 3, "motorcycle": 15, "person": 20},
                    "avg_occupancy": 0.75,
                    "congestion_level": "heavy",
                },
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["received_count"] == 2
    assert data["processed_count"] == 2


def test_ingest_nonexistent_camera(client, db):
    """Test ingesting event for non-existent camera."""
    fake_camera_id = uuid.uuid4()
    response = client.post(
        "/api/ingest/events",
        json={
            "events": [
                {
                    "camera_id": str(fake_camera_id),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "period_seconds": 300,
                    "counts": {"car": 10, "bus": 1, "truck": 0, "motorcycle": 2, "person": 5},
                    "avg_occupancy": 0.1,
                    "congestion_level": "free",
                }
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["received_count"] == 1
    assert data["processed_count"] == 0
    assert data["status"] == "partial"


def test_ingest_creates_alert_on_congestion(client, db):
    """Test that high congestion creates alert."""
    # Create test site and camera
    site = Site(
        name="Alert Test Site",
        slug="alert-test-site",
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
        name="Alert Test Camera",
        stream_url="rtsp://alert.example.com",
        status=CameraStatus.offline,
    )
    db.add(camera)
    db.commit()

    # Ingest heavy congestion event
    response = client.post(
        "/api/ingest/events",
        json={
            "events": [
                {
                    "camera_id": str(camera.id),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "period_seconds": 300,
                    "counts": {
                        "car": 150,
                        "bus": 10,
                        "truck": 5,
                        "motorcycle": 30,
                        "person": 50,
                    },
                    "avg_occupancy": 0.95,
                    "congestion_level": "blocked",
                }
            ]
        },
    )
    assert response.status_code == 200
    assert response.json()["processed_count"] == 1

    # Check that alert was created
    from app.models.alert import Alert
    alerts = db.query(Alert).filter(Alert.camera_id == camera.id).all()
    assert len(alerts) > 0
    assert alerts[0].alert_type.value == "congestion"
    assert alerts[0].severity.value == "critical"
