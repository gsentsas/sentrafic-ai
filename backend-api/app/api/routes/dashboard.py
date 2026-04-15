from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.api.deps import get_db
from app.services.site_service import get_site_count
from app.services.camera_service import get_camera_count
from app.services.traffic_service import get_total_vehicles_today, get_traffic_summary
from app.services.alert_service import get_unresolved_count, get_critical_alerts
from app.services.health_service import get_cameras_health_summary
from app.models.traffic_aggregate import TrafficAggregate
from app.models.camera import Camera, CameraStatus
from app.models.site import Site

router = APIRouter()


@router.get("/overview")
def dashboard_overview(db: Session = Depends(get_db)):
    """Vue d'ensemble du tableau de bord avec indicateurs cles."""
    total_sites = get_site_count(db)
    total_cameras = get_camera_count(db)
    cameras_online = get_camera_count(db, is_online=True)
    cameras_offline = get_camera_count(db, is_online=False)
    total_vehicles = get_total_vehicles_today(db)
    unresolved_alerts = get_unresolved_count(db)
    critical_count = get_unresolved_count(db, severity="critical")
    recent_alerts = get_critical_alerts(db, limit=5)
    cameras_health = get_cameras_health_summary(db)

    # Congestion summary from last hour
    summary_1h = get_traffic_summary(db, period_minutes=60)

    # Traffic trend: last 24h by hour
    now = datetime.now(timezone.utc)
    trend_start = now - timedelta(hours=24)
    trend_data = (
        db.query(TrafficAggregate)
        .filter(TrafficAggregate.timestamp >= trend_start)
        .order_by(TrafficAggregate.timestamp)
        .all()
    )

    # Aggregate by hour
    hourly = {}
    for agg in trend_data:
        hour_key = agg.timestamp.replace(minute=0, second=0, microsecond=0).isoformat()
        hourly[hour_key] = hourly.get(hour_key, 0) + agg.total_count

    traffic_trend_24h = [
        {"timestamp": k, "count": v} for k, v in sorted(hourly.items())
    ]

    # Watchlist: cameras offline or with errors
    problem_cameras = (
        db.query(Camera)
        .filter(Camera.status.in_([CameraStatus.offline, CameraStatus.error]), Camera.is_active == True)
        .limit(5)
        .all()
    )
    watchlist = [
        {
            "camera_id": str(c.id),
            "camera_name": c.name,
            "status": c.status.value,
            "last_seen_at": c.last_seen_at.isoformat() if c.last_seen_at else None,
        }
        for c in problem_cameras
    ]

    return {
        "summary": {
            "total_sites": total_sites,
            "total_cameras": total_cameras,
            "cameras_online": cameras_online,
            "cameras_offline": cameras_offline,
            "online_percentage": cameras_health.get("online_percentage", 0),
            "total_vehicles_today": total_vehicles,
            "alerts_unresolved": unresolved_alerts,
            "alerts_critical": critical_count,
        },
        "congestion": {
            "avg_level": summary_1h.get("avg_congestion_level", "free"),
            "total_vehicles_1h": summary_1h.get("total_vehicles", 0),
            "by_class": summary_1h.get("by_class", {}),
        },
        "recent_alerts": recent_alerts,
        "traffic_trend_24h": traffic_trend_24h,
        "watchlist": watchlist,
        "timestamp": now.isoformat(),
    }


@router.get("/live-summary")
def dashboard_live_summary(
    site_id: UUID | None = Query(default=None),
    status: CameraStatus | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Lightweight live payload for /live page (single polling endpoint)."""
    now = datetime.now(timezone.utc)
    latest_agg_timestamps = (
        db.query(
            TrafficAggregate.camera_id.label("camera_id"),
            func.max(TrafficAggregate.timestamp).label("latest_timestamp"),
        )
        .group_by(TrafficAggregate.camera_id)
        .subquery()
    )

    cameras_query = (
        db.query(Camera, Site)
        .join(Site, Site.id == Camera.site_id)
        .filter(Camera.is_active == True)
    )
    if site_id:
        cameras_query = cameras_query.filter(Camera.site_id == site_id)
    if status:
        cameras_query = cameras_query.filter(Camera.status == status)

    cameras = cameras_query.order_by(Camera.name.asc()).all()

    latest_aggregates = (
        db.query(TrafficAggregate)
        .join(
            latest_agg_timestamps,
            and_(
                TrafficAggregate.camera_id == latest_agg_timestamps.c.camera_id,
                TrafficAggregate.timestamp == latest_agg_timestamps.c.latest_timestamp,
            ),
        )
        .all()
    )
    latest_by_camera = {str(agg.camera_id): agg for agg in latest_aggregates}

    items = []
    for camera, site in cameras:
        last_agg = latest_by_camera.get(str(camera.id))
        reading_timestamp = last_agg.timestamp if last_agg else None
        is_stale = True
        if reading_timestamp:
            # SQLite retourne des datetimes naive — normaliser en UTC
            ts = reading_timestamp
            if ts.tzinfo is None:
                from datetime import timezone as _tz
                ts = ts.replace(tzinfo=_tz.utc)
            is_stale = (now - ts).total_seconds() >= 30
        items.append(
            {
                "camera_id": str(camera.id),
                "camera_name": camera.name,
                "site_name": site.name if site else None,
                "status": camera.status.value if hasattr(camera.status, "value") else camera.status,
                "stream_url": camera.stream_url,
                "last_seen_at": camera.last_seen_at.isoformat() if camera.last_seen_at else None,
                "last_reading": {
                    "total_count": last_agg.total_count if last_agg else 0,
                    "congestion_level": (
                        last_agg.congestion_level.value
                        if last_agg and hasattr(last_agg.congestion_level, "value")
                        else (last_agg.congestion_level if last_agg else "free")
                    ),
                    "avg_occupancy": last_agg.avg_occupancy if last_agg else 0.0,
                    "timestamp": reading_timestamp.isoformat() if reading_timestamp else None,
                    "is_stale": is_stale,
                }
                if last_agg
                else None,
            }
        )

    return {"cameras": items, "timestamp": now.isoformat()}
