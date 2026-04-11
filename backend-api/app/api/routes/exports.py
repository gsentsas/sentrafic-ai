from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
import io

from app.api.deps import get_db
from app.services.export_service import export_traffic_csv

router = APIRouter()


@router.get("/traffic.csv")
def export_traffic(
    db: Session = Depends(get_db),
    camera_id: UUID = Query(None),
    site_id: UUID = Query(None),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
):
    """
    Download traffic data as CSV.

    - **camera_id**: Filter by camera ID (optional)
    - **site_id**: Filter by site ID (optional)
    - **start_date**: Start timestamp (optional)
    - **end_date**: End timestamp (optional)

    Returns a CSV file with columns:
    Timestamp, Camera ID, Camera Name, Site Name, Period, Car Count, Bus Count,
    Truck Count, Motorcycle Count, Person Count, Total Count, Avg Occupancy,
    Congestion Level
    """
    csv_content = export_traffic_csv(
        db,
        camera_id=camera_id,
        site_id=site_id,
        start_date=start_date,
        end_date=end_date,
    )

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=traffic_export.csv"},
    )
