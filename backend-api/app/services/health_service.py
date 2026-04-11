import redis
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.database import engine
from app.core.config import settings
from app.models.camera import Camera, CameraStatus


def check_database_health() -> dict:
    """Check database connectivity."""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return {"status": "ok", "database": "PostgreSQL"}
    except Exception as e:
        return {"status": "error", "database": str(e)}


def check_redis_health() -> dict:
    """Check Redis connectivity."""
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        return {"status": "ok", "redis": "Connected"}
    except Exception as e:
        return {"status": "error", "redis": str(e)}


def get_system_health() -> dict:
    """Get overall system health status."""
    db_health = check_database_health()
    redis_health = check_redis_health()

    overall_status = "ok"
    if db_health["status"] == "error" or redis_health["status"] == "error":
        overall_status = "error"

    return {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "database": db_health,
            "cache": redis_health,
        },
    }


def get_cameras_health_summary(db: Session) -> dict:
    """Get summary of camera health status."""
    total_cameras = db.query(Camera).count()
    online_cameras = db.query(Camera).filter(Camera.status == CameraStatus.online).count()
    offline_cameras = db.query(Camera).filter(Camera.status == CameraStatus.offline).count()
    error_cameras = db.query(Camera).filter(Camera.status == CameraStatus.error).count()

    return {
        "total": total_cameras,
        "online": online_cameras,
        "offline": offline_cameras,
        "error": error_cameras,
        "online_percentage": (
            round((online_cameras / total_cameras) * 100, 2)
            if total_cameras > 0
            else 0
        ),
    }
