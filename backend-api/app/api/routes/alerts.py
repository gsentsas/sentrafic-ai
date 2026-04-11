from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db
from app.schemas.alert import AlertResponse, AlertResolve
from app.services.alert_service import (
    list_alerts,
    get_alert,
    resolve_alert,
)

router = APIRouter()


@router.get("/", response_model=list)
def get_alerts(
    db: Session = Depends(get_db),
    is_resolved: bool = Query(False),
    severity: str = Query(None),
    site_id: UUID = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get alerts with filtering.

    - **is_resolved**: Filter resolved status (default: False - unresolved)
    - **severity**: Filter by severity (optional)
    - **site_id**: Filter by site ID (optional)
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    return list_alerts(
        db,
        is_resolved=is_resolved,
        severity=severity,
        site_id=site_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert_by_id(
    alert_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a specific alert."""
    return get_alert(db, alert_id)


@router.post("/{alert_id}/resolve")
def resolve_alert_endpoint(
    alert_id: UUID,
    alert_resolve: AlertResolve,
    db: Session = Depends(get_db),
):
    """
    Resolve an alert.

    - **alert_id**: Alert ID to resolve
    - **resolved_by**: User ID who is resolving (optional)
    """
    alert = resolve_alert(db, alert_id, resolved_by=alert_resolve.resolved_by)
    return {
        "id": alert.id,
        "is_resolved": alert.is_resolved,
        "resolved_at": alert.resolved_at,
        "resolved_by": alert.resolved_by,
        "message": "Alert resolved successfully",
    }
