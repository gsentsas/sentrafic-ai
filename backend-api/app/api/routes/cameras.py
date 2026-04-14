from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta, timezone

from app.api.deps import get_db
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse
from app.services.camera_service import (
    list_cameras,
    get_camera,
    create_camera,
    update_camera,
)
from app.services.traffic_service import get_traffic_trend, get_traffic_summary, get_class_distribution
from app.services.alert_service import list_alerts
from app.models.camera import Camera
from app.models.site import Site
from app.models.traffic_aggregate import TrafficAggregate

router = APIRouter()


@router.get("/", response_model=list)
def get_cameras(
    db: Session = Depends(get_db),
    site_id: UUID = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get list of cameras.

    - **site_id**: Filter by site ID (optional)
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    return list_cameras(db, site_id=site_id, skip=skip, limit=limit)


@router.post("/", response_model=CameraResponse)
def create_new_camera(
    camera_create: CameraCreate,
    db: Session = Depends(get_db),
):
    """Create a new camera."""
    camera = create_camera(db, camera_create)
    site = db.query(Site).filter(Site.id == camera.site_id).first()
    return CameraResponse(
        id=camera.id,
        site_id=camera.site_id,
        name=camera.name,
        stream_url=camera.stream_url,
        status=camera.status.value,
        location_description=camera.location_description,
        is_active=camera.is_active,
        site_name=site.name if site else None,
    )


@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera_by_id(
    camera_id: UUID,
    db: Session = Depends(get_db),
):
    """Get details of a specific camera."""
    return get_camera(db, camera_id)


@router.put("/{camera_id}", response_model=CameraResponse)
def update_camera_by_id(
    camera_id: UUID,
    camera_update: CameraUpdate,
    db: Session = Depends(get_db),
):
    """Update a camera."""
    camera = update_camera(db, camera_id, camera_update)
    site = db.query(Site).filter(Site.id == camera.site_id).first()
    return CameraResponse(
        id=camera.id,
        site_id=camera.site_id,
        name=camera.name,
        stream_url=camera.stream_url,
        status=camera.status.value,
        location_description=camera.location_description,
        is_active=camera.is_active,
        site_name=site.name if site else None,
    )


@router.get("/{camera_id}/traffic")
def get_camera_traffic(
    camera_id: UUID,
    db: Session = Depends(get_db),
    hours: int = Query(24, ge=1, le=168, description="Hours of history to return"),
):
    """
    Get traffic data + KPIs for a specific camera.

    Returns:
    - trend: hourly vehicle counts for the past N hours
    - summary: current hour summary
    - distribution: vehicle class breakdown
    - recent_alerts: latest 5 alerts for this camera
    """
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera introuvable")

    trend_raw = get_traffic_trend(db, camera_id=camera_id, hours=hours)
    # Flatten to list of {timestamp, count} for frontend chart
    trend = [
        {"timestamp": str(p["timestamp"]), "count": p["total_count"]}
        for p in trend_raw.get("points", [])
    ]
    summary = get_traffic_summary(db, camera_id=camera_id, period_minutes=60)
    distribution = get_class_distribution(db, camera_id=camera_id, period_hours=24)

    # Last 5 alerts for this camera
    raw_alerts = list_alerts(db, camera_id=camera_id, skip=0, limit=5)
    recent_alerts = []
    for a in raw_alerts:
        if isinstance(a, dict):
            created_at = a.get("created_at")
            created_at_iso = created_at.isoformat() if hasattr(created_at, "isoformat") else created_at
            recent_alerts.append(
                {
                    "id": str(a.get("id")),
                    "alert_type": a.get("alert_type"),
                    "severity": a.get("severity"),
                    "message": a.get("message"),
                    "is_resolved": a.get("is_resolved"),
                    "created_at": created_at_iso,
                }
            )
            continue

        recent_alerts.append(
            {
                "id": str(a.id),
                "alert_type": a.alert_type.value if hasattr(a.alert_type, "value") else a.alert_type,
                "severity": a.severity.value if hasattr(a.severity, "value") else a.severity,
                "message": a.message,
                "is_resolved": a.is_resolved,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
        )

    # Last reading
    last_agg = (
        db.query(TrafficAggregate)
        .filter(TrafficAggregate.camera_id == camera_id)
        .order_by(TrafficAggregate.timestamp.desc())
        .first()
    )

    return {
        "camera_id": str(camera_id),
        "camera_name": camera.name,
        "status": camera.status.value if hasattr(camera.status, "value") else camera.status,
        "last_seen_at": camera.last_seen_at.isoformat() if camera.last_seen_at else None,
        "trend": trend,
        "summary": summary,
        "distribution": distribution,
        "recent_alerts": recent_alerts,
        "last_reading": {
            "total_count": last_agg.total_count if last_agg else 0,
            "congestion_level": (last_agg.congestion_level.value if last_agg and hasattr(last_agg.congestion_level, "value") else (last_agg.congestion_level if last_agg else "free")),
            "avg_occupancy": last_agg.avg_occupancy if last_agg else 0.0,
            "timestamp": last_agg.timestamp.isoformat() if last_agg and last_agg.timestamp else None,
        } if last_agg else None,
    }
