from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, date, timezone
from typing import Optional

from app.api.deps import get_db
from app.services.traffic_service import (
    get_traffic_aggregates,
    get_traffic_summary,
    get_traffic_trend,
    get_class_distribution,
)

router = APIRouter()


def _to_datetime(d: Optional[date]) -> Optional[datetime]:
    """Convert a date to a timezone-aware datetime (start of day UTC)."""
    if d is None:
        return None
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)


@router.get("/traffic")
def get_traffic_data(
    db: Session = Depends(get_db),
    camera_id: UUID = Query(None),
    site_id: UUID = Query(None),
    start_date: Optional[date] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[date] = Query(None, description="End date YYYY-MM-DD"),
    granularity: str = Query("hour", description="Aggregation granularity (ignored — kept for frontend compat)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get traffic aggregates with filters.

    - **camera_id**: Filter by camera ID (optional)
    - **site_id**: Filter by site ID (optional)
    - **start_date**: Start timestamp (optional)
    - **end_date**: End timestamp (optional)
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    aggregates = get_traffic_aggregates(
        db,
        camera_id=camera_id,
        site_id=site_id,
        start_date=_to_datetime(start_date),
        end_date=_to_datetime(end_date),
        skip=skip,
        limit=limit,
    )

    return [
        {
            "id": agg.id,
            "camera_id": agg.camera_id,
            "timestamp": agg.timestamp,
            "period_seconds": agg.period_seconds,
            "car_count": agg.car_count,
            "bus_count": agg.bus_count,
            "truck_count": agg.truck_count,
            "motorcycle_count": agg.motorcycle_count,
            "person_count": agg.person_count,
            "total_count": agg.total_count,
            "avg_occupancy": agg.avg_occupancy,
            "congestion_level": agg.congestion_level.value,
        }
        for agg in aggregates
    ]


@router.get("/summary")
def get_traffic_summary_endpoint(
    db: Session = Depends(get_db),
    camera_id: UUID = Query(None),
    site_id: UUID = Query(None),
    period_minutes: int = Query(60, ge=1),
):
    """
    Get traffic summary for a period.

    - **camera_id**: Filter by camera ID (optional)
    - **site_id**: Filter by site ID (optional)
    - **period_minutes**: Period to summarize (default: 60)
    """
    return get_traffic_summary(
        db,
        camera_id=camera_id,
        site_id=site_id,
        period_minutes=period_minutes,
    )


@router.get("/trend")
def get_traffic_trend_endpoint(
    camera_id: UUID,
    db: Session = Depends(get_db),
    hours: int = Query(24, ge=1, le=168),
):
    """
    Get traffic trend for a camera.

    - **camera_id**: Camera ID (required)
    - **hours**: Number of hours to trend (default: 24, max: 168)
    """
    return get_traffic_trend(db, camera_id=camera_id, hours=hours)


@router.get("/distribution")
def get_distribution(
    db: Session = Depends(get_db),
    camera_id: UUID = Query(None),
    site_id: UUID = Query(None),
    period_hours: int = Query(24, ge=1),
):
    """
    Get vehicle class distribution.

    - **camera_id**: Filter by camera ID (optional)
    - **site_id**: Filter by site ID (optional)
    - **period_hours**: Period to analyze (default: 24)
    """
    return get_class_distribution(
        db,
        camera_id=camera_id,
        site_id=site_id,
        period_hours=period_hours,
    )
