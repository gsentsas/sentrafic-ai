from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from datetime import datetime, timezone
from uuid import UUID

from app.models.alert import Alert, AlertType, AlertSeverity, ALERT_DESCRIPTIONS
from app.models.camera import Camera
from app.models.site import Site


def _serialize_alert(alert: Alert, camera: Camera = None, site: Site = None) -> dict:
    """Serialize an alert to a dict with enriched fields."""
    atype = alert.alert_type.value if isinstance(alert.alert_type, AlertType) else alert.alert_type
    info = ALERT_DESCRIPTIONS.get(atype, {})
    return {
        "id": alert.id,
        "camera_id": alert.camera_id,
        "site_id": alert.site_id,
        "alert_type": atype,
        "severity": alert.severity.value if isinstance(alert.severity, AlertSeverity) else alert.severity,
        "message": alert.message,
        "short_description": info.get("label", atype),
        "recommended_action": info.get("action", ""),
        "is_resolved": alert.is_resolved,
        "resolved_at": alert.resolved_at,
        "resolved_by": alert.resolved_by,
        "created_at": alert.created_at,
        "site_name": site.name if site else None,
        "camera_name": camera.name if camera else None,
    }


def list_alerts(
    db: Session,
    is_resolved: bool = None,
    severity: str = None,
    alert_type: str = None,
    site_id: UUID = None,
    camera_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
):
    """List alerts with filtering."""
    query = db.query(Alert)

    if is_resolved is not None:
        query = query.filter(Alert.is_resolved == is_resolved)
    if severity:
        query = query.filter(Alert.severity == severity)
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if site_id:
        query = query.filter(Alert.site_id == site_id)
    if camera_id:
        query = query.filter(Alert.camera_id == camera_id)

    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for alert in alerts:
        camera = db.query(Camera).filter(Camera.id == alert.camera_id).first()
        site = db.query(Site).filter(Site.id == alert.site_id).first()
        result.append(_serialize_alert(alert, camera, site))

    return result


def get_alert(db: Session, alert_id: UUID):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerte introuvable")
    camera = db.query(Camera).filter(Camera.id == alert.camera_id).first()
    site = db.query(Site).filter(Site.id == alert.site_id).first()
    return _serialize_alert(alert, camera, site)


def create_alert(
    db: Session,
    camera_id: UUID,
    site_id: UUID,
    alert_type: str,
    message: str,
    severity: str = "warning",
) -> Alert:
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


def resolve_alert(db: Session, alert_id: UUID, resolved_by: UUID = None) -> dict:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerte introuvable")

    alert.is_resolved = True
    alert.resolved_at = datetime.now(timezone.utc)
    alert.resolved_by = resolved_by
    db.add(alert)
    db.commit()
    db.refresh(alert)

    camera = db.query(Camera).filter(Camera.id == alert.camera_id).first()
    site = db.query(Site).filter(Site.id == alert.site_id).first()
    return _serialize_alert(alert, camera, site)


def get_unresolved_count(db: Session, site_id: UUID = None, severity: str = None) -> int:
    query = db.query(func.count(Alert.id)).filter(Alert.is_resolved == False)
    if site_id:
        query = query.filter(Alert.site_id == site_id)
    if severity:
        query = query.filter(Alert.severity == severity)
    return query.scalar() or 0


def get_critical_alerts(db: Session, limit: int = 10):
    """Get recent unresolved alerts (all severities, critical first)."""
    alerts = (
        db.query(Alert)
        .filter(Alert.is_resolved == False)
        .order_by(Alert.severity.desc(), Alert.created_at.desc())
        .limit(limit)
        .all()
    )
    result = []
    for alert in alerts:
        camera = db.query(Camera).filter(Camera.id == alert.camera_id).first()
        site = db.query(Site).filter(Site.id == alert.site_id).first()
        result.append(_serialize_alert(alert, camera, site))
    return result
