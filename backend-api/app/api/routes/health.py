from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.health_service import (
    get_system_health,
    get_cameras_health_summary,
)

router = APIRouter()


@router.get("/")
def health_check():
    """
    System health check endpoint (no authentication required).

    Returns status of database, cache, and other services.
    """
    return get_system_health()


@router.get("/cameras")
def cameras_health(db: Session = Depends(get_db)):
    """Get summary of camera health status."""
    return get_cameras_health_summary(db)
