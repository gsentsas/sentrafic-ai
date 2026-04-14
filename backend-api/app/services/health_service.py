import redis
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.database import engine
from app.core.config import settings
from app.models.camera import Camera, CameraStatus


def check_database_health() -> dict:
    """Check database connectivity."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "detail": "PostgreSQL connecté"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def check_redis_health() -> dict:
    """Check Redis connectivity."""
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        return {"status": "ok", "detail": "Redis connecté"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def get_system_health() -> dict:
    """Get overall system health status."""
    db_health = check_database_health()
    redis_health = check_redis_health()

    overall = "ok"
    if db_health["status"] == "error" or redis_health["status"] == "error":
        overall = "degraded" if db_health["status"] == "ok" else "error"

    return {
        "status": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0-mvp",
        "services": {
            "database": db_health,
            "cache": redis_health,
        },
    }


def get_cameras_health_summary(db: Session) -> dict:
    """Get summary of camera health status."""
    total = db.query(Camera).filter(Camera.is_active == True).count()
    online = db.query(Camera).filter(
        Camera.status == CameraStatus.online, Camera.is_active == True
    ).count()
    offline = db.query(Camera).filter(
        Camera.status == CameraStatus.offline, Camera.is_active == True
    ).count()
    error = db.query(Camera).filter(
        Camera.status == CameraStatus.error, Camera.is_active == True
    ).count()

    return {
        "total": total,
        "online": online,
        "offline": offline,
        "error": error,
        "online_percentage": round((online / total) * 100, 1) if total > 0 else 0,
    }
