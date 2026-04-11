from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from datetime import datetime, timezone
from uuid import UUID

from app.models.alert import Alert, AlertType, AlertSeverity
from app.models.camera import Camera
from app.models.site import Site


def list_alerts(
    db: Session,
    is_resolved: bool = False,
    severity: str = None,
    site_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
):
    """List alerts with filtering."""
    query = db.query(Alert).filter(Alert.is_resolved == is_resolved)

    if severity:
        query = query.filter(Alert.severity == severity)

    if site_id:
        query = query.filter(Alert.site_id == site_id)

    alerts = (
        query.order_by(Alert.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for alert in alerts:
        camera = db.query(Camera).filter(Camera.id == alert.camera_id).first()
        site = db.query(Site).filter(Site.id == alert.site_id).first()

        result.append({
            "id": alert.id,
            "camera_id": alert.camera_id,
            "site_id": alert.site_id,
            "alert_type": alert.alert_type.value,
            "severity": alert.severity.value,
            "message": alert.message,
            "is_resolved": alert.is_resolved,
            "resolved_at": alert.resolved_at,
            "resolved_by": alert.resolved_by,
            "created_at": alert.created_at,
            "site_name": site.name if site else None,
            "camera_name": camera.name if camera else None,
        })

    return result


def get_alert(db: Session, alert_id: UUID):
    """Get a single alert by ID."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    camera = db.query(Camera).filter(Camera.id == alert.camera_id).first()
    site = db.query(Site).filter(Site.id == alert.site_id).first()

    return {
        "id": alert.id,
        "camera_id": alert.camera_id,
        "site_id": alert.site_id,
        "alert_type": alert.alert_type.value,
        "severity": alert.severity.value,
        "message": alert.message,
        "is_resolved": alert.is_resolved,
        "resolved_at": alert.resolved_at,
        "resolved_by": alert.resolved_by,
        "created_at": alert.created_at,
        "site_name": site.name if site else None,
        "camera_name": camera.name if camera else None,
    }


def create_alert(
    db: Session,
    camera_id: UUID,
    site_id: UUID,
    alert_type: str,
    message: str,
    severity: str = "warning",
) -> Alert:
    """Create a new alert."""
    alert = Alert(
        camera_id=camera_id,
        site_id=site_id,
        alert_type=AlertType(alert_type),
        severity=AlertSeverity(severity),
        message=message,
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def resolve_alert(
    db: Session,
    alert_id: UUID,
    resolved_by: UUID = None,
) -> Alert:
    """Resolve an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    alert.is_resolved = True
    alert.resolved_at = datetime.now(timezone.utc)
    alert.resolved_by = resolved_by

    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_unresolved_count(
    db: Session,
    site_id: UUID = None,
    severity: str = None,
) -> int:
    """Get count of unresolved alerts."""
    query = db.query(func.count(Alert.id)).filter(Alert.is_resolved == False)

    if site_id:
        query = query.filter(Alert.site_id == site_id)

    if severity:
        query = query.filter(Alert.severity == severity)

    return query.scalar() or 0


def get_critical_alerts(db: Session, limit: int = 10):
    """Get recent critical alerts."""
    alerts = (
        db.query(Alert)
        .filter(Alert.is_resolved == False, Alert.severity == AlertSeverity.critical)
        .order_by(Alert.created_at.desc())
        .limit(limit)
        .all()
    )

    result = []
    for alert in alerts:
        camera = db.query(Camera).filter(Camera.id == alert.camera_id).first()
        site = db.query(Site).filter(Site.id == alert.site_id).first()

        result.append({
            "id": alert.id,
            "camera_id": alert.camera_id,
            "site_id": alert.site_id,
            "alert_type": alert.alert_type.value,
            "severity": alert.severity.value,
            "message": alert.message,
            "created_at": alert.created_at,
            "site_name": site.name if site else None,
            "camera_name": camera.name if camera else None,
        })

    return result
