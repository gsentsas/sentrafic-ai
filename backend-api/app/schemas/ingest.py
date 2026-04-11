from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Dict


class IngestEvent(BaseModel):
    """Single event from vision engine."""
    camera_id: UUID = Field(..., description="Camera ID")
    timestamp: datetime = Field(..., description="Event timestamp")
    period_seconds: int = Field(..., description="Aggregation period in seconds")
    counts: Dict[str, int] = Field(..., description="Count by class (car, bus, truck, motorcycle, person)")
    avg_occupancy: float = Field(default=0.0, description="Average occupancy 0-1")
    congestion_level: str = Field(default="free", description="Congestion level")


class IngestBatch(BaseModel):
    """Batch of events from vision engine."""
    events: List[IngestEvent] = Field(..., description="List of detection events")


class IngestResponse(BaseModel):
    """Response after ingesting events."""
    received_count: int = Field(..., description="Number of events received")
    processed_count: int = Field(..., description="Number of events processed")
    status: str = Field(default="success", description="Processing status")
    message: str = Field(default="", description="Response message")
