from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date, datetime, timezone
from typing import Optional

from app.api.deps import get_db
from app.services.export_service import export_traffic_csv

router = APIRouter()


def _to_datetime(d: Optional[date], end_of_day: bool = False) -> Optional[datetime]:
    """Convertit une date YYYY-MM-DD en datetime UTC."""
    if d is None:
        return None
    if end_of_day:
        return datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=timezone.utc)
    return datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=timezone.utc)


@router.get("/traffic.csv")
def export_traffic(
    db: Session = Depends(get_db),
    camera_id: Optional[UUID] = Query(None, description="Filtrer par caméra"),
    site_id: Optional[UUID] = Query(None, description="Filtrer par site"),
    start_date: Optional[date] = Query(None, description="Date de début YYYY-MM-DD"),
    end_date: Optional[date] = Query(None, description="Date de fin YYYY-MM-DD"),
):
    """
    Télécharger les données trafic au format CSV.

    Paramètres optionnels :
    - **camera_id** : filtrer par caméra
    - **site_id** : filtrer par site
    - **start_date** : date de début (YYYY-MM-DD)
    - **end_date** : date de fin (YYYY-MM-DD)

    Colonnes retournées :
    Timestamp, Camera ID, Camera Name, Site Name, Period (s),
    Car Count, Bus Count, Truck Count, Motorcycle Count, Person Count,
    Total Count, Avg Occupancy, Congestion Level
    """
    csv_content = export_traffic_csv(
        db,
        camera_id=camera_id,
        site_id=site_id,
        start_date=_to_datetime(start_date),
        end_date=_to_datetime(end_date, end_of_day=True),
    )

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=trafic_export.csv"},
    )
