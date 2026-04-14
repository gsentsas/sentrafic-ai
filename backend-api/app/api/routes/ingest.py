from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.schemas.ingest import IngestBatch, IngestResponse
from app.services.ingest_service import process_ingest_batch

router = APIRouter()


@router.post("/events", response_model=IngestResponse)
def ingest_events(
    batch: IngestBatch,
    db: Session = Depends(get_db),
    _api_key: str = Depends(require_api_key),
):
    """
    Receive detection events batch from vision engine.

    Requires X-API-Key header matching VISION_API_KEY config.

    Expected payload:
    ```json
    {
      "events": [
        {
          "camera_id": "uuid",
          "timestamp": "2024-01-15T10:30:00Z",
          "period_seconds": 300,
          "counts": {
            "car": 45,
            "bus": 3,
            "truck": 2,
            "motorcycle": 8,
            "person": 12
          },
          "avg_occupancy": 0.65,
          "congestion_level": "moderate"
        }
      ]
    }
    ```
    """
    result = process_ingest_batch(db, batch.events)
    return IngestResponse(
        received_count=result["received_count"],
        processed_count=result["processed_count"],
        status=result["status"],
        message=f"Processed {result['processed_count']}/{result['received_count']} events",
    )
