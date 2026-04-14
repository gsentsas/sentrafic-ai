import redis
from fastapi import HTTPException, status, Security
from fastapi.security import APIKeyHeader

from app.core.database import get_db  # noqa: F401 — re-exported for routes
from app.core.config import settings
from app.core.security import get_current_user  # noqa: F401 – re-exported for routes

# Header scheme for vision-engine API key auth
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_redis():
    """Yield a Redis connection."""
    try:
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        yield r
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de cache indisponible",
        )


def require_api_key(api_key: str = Security(_api_key_header)):
    """Dependency: require a valid X-API-Key header (for vision-engine routes)."""
    if not api_key or api_key != settings.VISION_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cle API invalide ou absente",
        )
    return api_key
