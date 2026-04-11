from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class AlertResponse(BaseModel):
    """Response model for alert information."""
    id: UUID = Field(..., description="Alert ID")
    camera_id: UUID = Field(..., description="Camera ID")
    site_id: UUID = Field(..., description="Site ID")
    alert_type: str = Field(..., description="Type of alert")
    severity: str = Field(..., description="Alert severity level")
    message: str = Field(..., description="Alert message")
    is_resolved: bool = Field(..., description="Is alert resolved")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    resolved_by: Optional[UUID] = Field(None, description="ID of user who resolved it")
    created_at: datetime = Field(..., description="Alert creation timestamp")
    site_name: Optional[str] = Field(None, description="Site name")
    camera_name: Optional[str] = Field(None, description="Camera name")

    class Config:
        from_attributes = True


class AlertResolve(BaseModel):
    """Request model for resolving an alert."""
    resolved_by: Optional[UUID] = Field(None, description="ID of user resolving the alert")
    note: Optional[str] = Field(None, description="Resolution note")
