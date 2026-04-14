from sqlalchemy.orm import Session
from datetime import datetime, timezone
from uuid import UUID

from app.models.traffic_aggregate import TrafficAggregate, CongestionLevel
from app.models.camera import Camera, CameraStatus
from app.models.camera_health import CameraHealthCheck, HealthStatus
from app.models.alert import Alert, AlertType, AlertSeverity
from app.services.alert_service import create_alert
from app.schemas.ingest import IngestEvent


CONGESTION_THRESHOLD = {
    "free": (0, 30),
    "moderate": (30, 60),
    "heavy": (60, 85),
    "blocked": (85, 100),
}


def process_ingest_event(db: Session, event: IngestEvent) -> TrafficAggregate:
    """Process a single ingest event and create traffic aggregate."""
    # Verify camera exists
    camera = db.query(Camera).filter(Camera.id == event.camera_id).first()
    if not camera:
        raise ValueError(f"Camera {event.camera_id} not found")

    # Update camera status and last_seen_at
    camera.status = CameraStatus.online
    camera.last_seen_at = datetime.now(timezone.utc)
    db.add(camera)

    # Extract counts from the event
    counts = event.counts or {}
    car_count = counts.get("car", 0)
    bus_count = counts.get("bus", 0)
    truck_count = counts.get("truck", 0)
    motorcycle_count = counts.get("motorcycle", 0)
    person_count = counts.get("person", 0)
    total_count = (
        car_count + bus_count + truck_count + motorcycle_count + person_count
    )

    # Create traffic aggregate
    aggregate = TrafficAggregate(
        camera_id=event.camera_id,
        timestamp=event.timestamp,
        period_seconds=event.period_seconds,
        car_count=car_count,
        bus_count=bus_count,
        truck_count=truck_count,
        motorcycle_count=motorcycle_count,
        person_count=person_count,
        total_count=total_count,
        avg_occupancy=event.avg_occupancy or 0.0,
        congestion_level=CongestionLevel(event.congestion_level),
    )

    db.add(aggregate)
    db.flush()

    # Create health check record
    health_check = CameraHealthCheck(
        camera_id=event.camera_id,
        status=HealthStatus.ok,
        last_frame_at=event.timestamp,
        checked_at=datetime.now(timezone.utc),
    )
    db.add(health_check)

    # Check for congestion alerts
    if event.congestion_level in ["heavy", "blocked"]:
        # Check if there's already an unresolved congestion alert for this camera
        existing_alert = (
            db.query(Alert)
            .filter(
                Alert.camera_id == event.camera_id,
                Alert.alert_type == AlertType.congestion,
                Alert.is_resolved == False,
            )
            .first()
        )

        if not existing_alert:
            severity = (
                AlertSeverity.critical
                if event.congestion_level == "blocked"
                else AlertSeverity.warning
            )
            message = (
                f"High congestion detected: {event.congestion_level.upper()} "
                f"({total_count} vehicles, {event.avg_occupancy*100:.1f}% occupancy)"
            )

            alert = Alert(
                camera_id=event.camera_id,
                site_id=camera.site_id,
                alert_type=AlertType.congestion,
                severity=severity,
                message=message,
            )
            db.add(alert)

    db.commit()
    db.refresh(aggregate)
    return aggregate


def process_ingest_batch(db: Session, events: list) -> dict:
    """Process a batch of ingest events."""
    received_count = len(events)
    processed_count = 0
    errors = []

    for event in events:
        try:
            process_ingest_event(db, event)
            processed_count += 1
        except Exception as e:
            errors.append(str(e))

    return {
        "received_count": received_count,
        "processed_count": processed_count,
        "status": "success" if processed_count == received_count else "partial",
        "errors": errors,
    }


def update_camera_offline(db: Session, camera_id: UUID):
    """Mark a camera as offline and create alert."""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        return

    if camera.status != CameraStatus.offline:
        camera.status = CameraStatus.offline
        db.add(camera)

        # Create offline alert if not already exists
        existing_alert = (
            db.query(Alert)
            .filter(
                Alert.camera_id == camera_id,
                Alert.alert_type == AlertType.camera_offline,
                Alert.is_resolved == False,
            )
            .first()
        )

        if not existing_alert:
            alert = Alert(
                camera_id=camera_id,
                site_id=camera.site_id,
                alert_type=AlertType.camera_offline,
                severity=AlertSeverity.critical,
                message=f"Camera '{camera.name}' has gone offline",
            )
            db.add(alert)

        db.commit()
