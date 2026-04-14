from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from uuid import UUID
from typing import List, Dict

from app.models.traffic_aggregate import TrafficAggregate, CongestionLevel
from app.models.camera import Camera
from app.models.site import Site


def get_traffic_aggregates(
    db: Session,
    camera_id: UUID = None,
    site_id: UUID = None,
    start_date: datetime = None,
    end_date: datetime = None,
    skip: int = 0,
    limit: int = 100,
):
    """Get traffic aggregates with filters."""
    query = db.query(TrafficAggregate)

    if camera_id:
        query = query.filter(TrafficAggregate.camera_id == camera_id)

    if site_id:
        # Join with camera to filter by site
        query = query.join(Camera).filter(Camera.site_id == site_id)

    if start_date:
        query = query.filter(TrafficAggregate.timestamp >= start_date)

    if end_date:
        query = query.filter(TrafficAggregate.timestamp <= end_date)

    aggregates = (
        query.order_by(TrafficAggregate.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return aggregates


def get_traffic_summary(
    db: Session,
    camera_id: UUID = None,
    site_id: UUID = None,
    period_minutes: int = 60,
):
    """Get traffic summary for a period."""
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(minutes=period_minutes)

    aggregates = get_traffic_aggregates(
        db,
        camera_id=camera_id,
        site_id=site_id,
        start_date=start_time,
        end_date=now,
        limit=1000,
    )

    total_cars = sum(a.car_count for a in aggregates)
    total_buses = sum(a.bus_count for a in aggregates)
    total_trucks = sum(a.truck_count for a in aggregates)
    total_motorcycles = sum(a.motorcycle_count for a in aggregates)
    total_persons = sum(a.person_count for a in aggregates)
    total_vehicles = total_cars + total_buses + total_trucks + total_motorcycles

    congestion_levels = [a.congestion_level.value for a in aggregates]
    if congestion_levels:
        from collections import Counter
        avg_congestion = Counter(congestion_levels).most_common(1)[0][0]
    else:
        avg_congestion = "free"

    return {
        "total_vehicles": total_vehicles,
        "by_class": {
            "car": total_cars,
            "bus": total_buses,
            "truck": total_trucks,
            "motorcycle": total_motorcycles,
            "person": total_persons,
        },
        "period_start": start_time,
        "period_end": now,
        "avg_congestion_level": avg_congestion,
    }


def get_traffic_trend(
    db: Session,
    camera_id: UUID,
    hours: int = 24,
):
    """Get traffic trend for a camera over a period."""
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=hours)

    aggregates = (
        db.query(TrafficAggregate)
        .filter(
            TrafficAggregate.camera_id == camera_id,
            TrafficAggregate.timestamp >= start_time,
            TrafficAggregate.timestamp <= now,
        )
        .order_by(TrafficAggregate.timestamp)
        .all()
    )

    points = [
        {
            "timestamp": agg.timestamp,
            "total_count": agg.total_count,
            "car_count": agg.car_count,
            "congestion_level": agg.congestion_level.value,
        }
        for agg in aggregates
    ]

    return {
        "camera_id": camera_id,
        "period": f"{hours}h",
        "points": points,
    }


def get_class_distribution(
    db: Session,
    camera_id: UUID = None,
    site_id: UUID = None,
    period_hours: int = 24,
):
    """Get vehicle class distribution for a period."""
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=period_hours)

    aggregates = get_traffic_aggregates(
        db,
        camera_id=camera_id,
        site_id=site_id,
        start_date=start_time,
        end_date=now,
        limit=10000,
    )

    total_cars = sum(a.car_count for a in aggregates)
    total_buses = sum(a.bus_count for a in aggregates)
    total_trucks = sum(a.truck_count for a in aggregates)
    total_motorcycles = sum(a.motorcycle_count for a in aggregates)
    total_persons = sum(a.person_count for a in aggregates)

    total = (
        total_cars + total_buses + total_trucks + total_motorcycles + total_persons
    )

    if total == 0:
        distribution = {
            "car": 0,
            "bus": 0,
            "truck": 0,
            "motorcycle": 0,
            "person": 0,
        }
    else:
        distribution = {
            "car": round((total_cars / total) * 100, 2),
            "bus": round((total_buses / total) * 100, 2),
            "truck": round((total_trucks / total) * 100, 2),
            "motorcycle": round((total_motorcycles / total) * 100, 2),
            "person": round((total_persons / total) * 100, 2),
        }

    return {
        "distribution": distribution,
        "total_count": total,
        "period_hours": period_hours,
    }


def get_total_vehicles_today(db: Session) -> int:
    """Get total vehicles detected today."""
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    today_end = today_start + timedelta(days=1)

    result = (
        db.query(func.sum(TrafficAggregate.total_count))
        .filter(
            TrafficAggregate.timestamp >= today_start,
            TrafficAggregate.timestamp < today_end,
        )
        .scalar()
    )

    return result or 0


def get_peak_congestion_hours(
    db: Session,
    camera_id: UUID = None,
    site_id: UUID = None,
    hours: int = 24,
) -> List[Dict]:
    """Get hours with peak congestion."""
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=hours)

    aggregates = get_traffic_aggregates(
        db,
        camera_id=camera_id,
        site_id=site_id,
        start_date=start_time,
        end_date=now,
        limit=10000,
    )

    # Group by hour and find average congestion
    hourly_data = {}
    for agg in aggregates:
        hour_key = agg.timestamp.replace(minute=0, second=0, microsecond=0)
        if hour_key not in hourly_data:
            hourly_data[hour_key] = {"total": 0, "count": 0}
        hourly_data[hour_key]["total"] += agg.total_count
        hourly_data[hour_key]["count"] += 1

    result = [
        {
            "hour": hour,
            "avg_traffic": int(data["total"] / data["count"]),
        }
        for hour, data in sorted(hourly_data.items())
    ]

    return result
