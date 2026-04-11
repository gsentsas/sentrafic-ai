import csv
import io
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.models.traffic_aggregate import TrafficAggregate
from app.models.camera import Camera
from app.models.site import Site


def export_traffic_csv(
    db: Session,
    camera_id: UUID = None,
    site_id: UUID = None,
    start_date: datetime = None,
    end_date: datetime = None,
) -> str:
    """Export traffic data as CSV."""
    query = db.query(TrafficAggregate)

    if camera_id:
        query = query.filter(TrafficAggregate.camera_id == camera_id)

    if site_id:
        query = query.join(Camera).filter(Camera.site_id == site_id)

    if start_date:
        query = query.filter(TrafficAggregate.timestamp >= start_date)

    if end_date:
        query = query.filter(TrafficAggregate.timestamp <= end_date)

    aggregates = query.order_by(TrafficAggregate.timestamp).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "Timestamp",
        "Camera ID",
        "Camera Name",
        "Site Name",
        "Period (seconds)",
        "Car Count",
        "Bus Count",
        "Truck Count",
        "Motorcycle Count",
        "Person Count",
        "Total Count",
        "Avg Occupancy",
        "Congestion Level",
    ])

    # Write data rows
    for agg in aggregates:
        camera = db.query(Camera).filter(Camera.id == agg.camera_id).first()
        site = None
        if camera:
            site = db.query(Site).filter(Site.id == camera.site_id).first()

        writer.writerow([
            agg.timestamp.isoformat(),
            str(agg.camera_id),
            camera.name if camera else "Unknown",
            site.name if site else "Unknown",
            agg.period_seconds,
            agg.car_count,
            agg.bus_count,
            agg.truck_count,
            agg.motorcycle_count,
            agg.person_count,
            agg.total_count,
            f"{agg.avg_occupancy:.2%}",
            agg.congestion_level.value,
        ])

    return output.getvalue()


def export_alerts_csv(
    db: Session,
    is_resolved: bool = None,
    start_date: datetime = None,
    end_date: datetime = None,
) -> str:
    """Export alerts as CSV."""
    from app.models.alert import Alert

    query = db.query(Alert)

    if is_resolved is not None:
        query = query.filter(Alert.is_resolved == is_resolved)

    if start_date:
        query = query.filter(Alert.created_at >= start_date)

    if end_date:
        query = query.filter(Alert.created_at <= end_date)

    alerts = query.order_by(Alert.created_at.desc()).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "Created At",
        "Alert Type",
        "Severity",
        "Site Name",
        "Camera Name",
        "Message",
        "Is Resolved",
        "Resolved At",
    ])

    # Write data rows
    for alert in alerts:
        camera = db.query(Camera).filter(Camera.id == alert.camera_id).first()
        site = db.query(Site).filter(Site.id == alert.site_id).first()

        writer.writerow([
            alert.created_at.isoformat(),
            alert.alert_type.value,
            alert.severity.value,
            site.name if site else "Unknown",
            camera.name if camera else "Unknown",
            alert.message,
            "Yes" if alert.is_resolved else "No",
            alert.resolved_at.isoformat() if alert.resolved_at else "",
        ])

    return output.getvalue()
