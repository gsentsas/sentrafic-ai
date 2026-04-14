import pytest
from datetime import datetime, timezone
import uuid

from app.models.site import Site, SiteType
from app.models.camera import Camera, CameraStatus


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _make_site(db, name="Test Site", slug="test-site"):
    site = Site(
        name=name, slug=slug,
        address="123 Rue Test", city="Dakar",
        latitude=14.7167, longitude=-17.4667,
        site_type=SiteType.intersection,
    )
    db.add(site)
    db.flush()
    return site


def _make_camera(db, site_id, name="Test Camera"):
    cam = Camera(
        site_id=site_id, name=name,
        stream_url="rtsp://test.example.com",
        status=CameraStatus.offline,
    )
    db.add(cam)
    db.flush()
    return cam


def _event(camera_id, congestion="free", car=45):
    return {
        "camera_id": str(camera_id),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "period_seconds": 300,
        "counts": {"car": car, "bus": 3, "truck": 2, "motorcycle": 8, "person": 12},
        "avg_occupancy": 0.65,
        "congestion_level": congestion,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_ingest_requires_api_key(client, db):
    """Ingest endpoint must reject requests without X-API-Key."""
    response = client.post("/api/ingest/events", json={"events": []})
    assert response.status_code == 403


def test_ingest_valid_event(ingest_client, db):
    """Test ingestion d'un événement valide."""
    site = _make_site(db)
    cam = _make_camera(db, site.id)
    db.commit()

    response = ingest_client.post("/api/ingest/events", json={"events": [_event(cam.id)]})
    assert response.status_code == 200
    data = response.json()
    assert data["received_count"] == 1
    assert data["processed_count"] == 1
    assert data["status"] == "success"


def test_ingest_multiple_events(ingest_client, db):
    """Test ingestion de plusieurs événements en batch."""
    site = _make_site(db, "Multi Site", "multi-site")
    cam1 = _make_camera(db, site.id, "Camera 1")
    cam2 = _make_camera(db, site.id, "Camera 2")
    db.commit()

    response = ingest_client.post(
        "/api/ingest/events",
        json={"events": [_event(cam1.id), _event(cam2.id)]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["received_count"] == 2
    assert data["processed_count"] == 2


def test_ingest_nonexistent_camera(ingest_client, db):
    """Ingestion sur une caméra inexistante → processed = 0, status = partial."""
    response = ingest_client.post(
        "/api/ingest/events",
        json={"events": [_event(uuid.uuid4())]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["received_count"] == 1
    assert data["processed_count"] == 0
    assert data["status"] == "partial"


def test_ingest_updates_camera_status(ingest_client, db):
    """Après ingest, la caméra doit passer en statut 'online'."""
    from app.models.camera import CameraStatus
    site = _make_site(db, "Status Site", "status-site")
    cam = _make_camera(db, site.id)
    db.commit()

    ingest_client.post("/api/ingest/events", json={"events": [_event(cam.id)]})

    db.refresh(cam)
    assert cam.status == CameraStatus.online


def test_ingest_creates_alert_on_heavy_congestion(ingest_client, db):
    """Congestion 'blocked' doit déclencher une alerte critique."""
    from app.models.alert import Alert
    site = _make_site(db, "Alert Site", "alert-site")
    cam = _make_camera(db, site.id)
    db.commit()

    ingest_client.post(
        "/api/ingest/events",
        json={"events": [_event(cam.id, congestion="blocked", car=200)]},
    )

    alerts = db.query(Alert).filter(Alert.camera_id == cam.id).all()
    assert len(alerts) > 0
    assert alerts[0].alert_type.value == "congestion"
    assert alerts[0].severity.value == "critical"


def test_ingest_empty_batch(ingest_client, db):
    """Batch vide → 0 reçu, 0 traité."""
    response = ingest_client.post("/api/ingest/events", json={"events": []})
    assert response.status_code == 200
    data = response.json()
    assert data["received_count"] == 0
    assert data["processed_count"] == 0
