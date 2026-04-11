from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.api.deps import get_db
from app.services.site_service import get_site_count
from app.services.camera_service import get_camera_count
from app.services.traffic_service import get_total_vehicles_today, get_traffic_trend
from app.services.alert_service import get_unresolved_count, get_critical_alerts

router = APIRouter()


@router.get("/overview")
def dashboard_overview(db: Session = Depends(get_db)):
    """
    Get dashboard overview with key metrics.

    Returns:
    - total_sites: Total number of sites
    - total_cameras: Total number of cameras
    - cameras_online: Number of online cameras
    - total_vehicles_today: Total vehicles detected today
    - alerts_unresolved: Count of unresolved alerts
    - congestion_summary: Current congestion status
    - recent_alerts: Last 5 critical alerts
    - traffic_trend_24h: 24-hour traffic trend
    """
    total_sites = get_site_count(db)
    total_cameras = get_camera_count(db)
    cameras_online = get_camera_count(db, is_online=True)
    total_vehicles = get_total_vehicles_today(db)
    unresolved_alerts = get_unresolved_count(db)
    critical_alerts = get_critical_alerts(db, limit=5)

    return {
        "summary": {
            "total_sites": total_sites,
            "total_cameras": total_cameras,
            "cameras_online": cameras_online,
            "cameras_offline": total_cameras - cameras_online,
            "online_percentage": (
                round((cameras_online / total_cameras) * 100, 2)
                if total_cameras > 0
                else 0
            ),
            "total_vehicles_today": total_vehicles,
        },
        "alerts": {
            "unresolved": unresolved_alerts,
            "critical": len([a for a in critical_alerts if a.get("severity") == "critical"]),
            "recent": critical_alerts,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
