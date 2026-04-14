from datetime import datetime, timezone

from app.models.site import Site, SiteType
from app.models.camera import Camera, CameraStatus
from app.models.alert import Alert, AlertType, AlertSeverity
from app.models.traffic_aggregate import TrafficAggregate, CongestionLevel


def _make_site(db, slug="cam-traffic-site"):
    site = Site(
        name="Camera Traffic Site",
        slug=slug,
        address="123 Test Address",
        city="Dakar",
        latitude=14.7167,
        longitude=-17.4667,
        site_type=SiteType.intersection,
    )
    db.add(site)
    db.flush()
    return site


def _make_camera(db, site_id):
    cam = Camera(
        site_id=site_id,
        name="Camera Traffic Test",
        stream_url="rtsp://camera.example.com/live",
        status=CameraStatus.online,
        is_active=True,
    )
    db.add(cam)
    db.flush()
    return cam


def test_camera_traffic_endpoint_handles_serialized_alerts(admin_client, db):
    site = _make_site(db)
    cam = _make_camera(db, site.id)

    db.add(
        TrafficAggregate(
            camera_id=cam.id,
            timestamp=datetime.now(timezone.utc),
            period_seconds=300,
            car_count=12,
            bus_count=1,
            truck_count=1,
            motorcycle_count=2,
            person_count=4,
            total_count=20,
            avg_occupancy=0.35,
            congestion_level=CongestionLevel.moderate,
        )
    )

    db.add(
        Alert(
            camera_id=cam.id,
            site_id=site.id,
            alert_type=AlertType.congestion,
            severity=AlertSeverity.warning,
            message="Congestion test",
            is_resolved=False,
        )
    )
    db.commit()

    response = admin_client.get(f"/api/cameras/{cam.id}/traffic?hours=24")
    assert response.status_code == 200
    data = response.json()
    assert data["camera_id"] == str(cam.id)
    assert isinstance(data["recent_alerts"], list)
    assert len(data["recent_alerts"]) >= 1
