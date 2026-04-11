import redis
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db as _get_db
from app.core.config import settings
from app.core.security import get_current_user as _get_current_user


def get_db() -> Session:
    """Get database session."""
    db = _get_db()
    try:
        yield next(db)
    finally:
        pass


def get_redis():
    """Get Redis connection."""
    try:
        r = redis.from_url(settings.REDIS_URL)
        yield r
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis connection failed",
        )


def get_current_user(token: str, db: Session = Depends(get_db)):
    """Get current authenticated user."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _get_current_user(token=token, db=db)
