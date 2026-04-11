from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class CameraCreate(BaseModel):
    """Request model for creating a camera."""
    site_id: UUID = Field(..., description="Site ID")
    name: str = Field(..., description="Camera name")
    stream_url: str = Field(..., description="Stream URL")
    location_description: Optional[str] = Field(None, description="Location description")


class CameraUpdate(BaseModel):
    """Request model for updating a camera."""
    name: Optional[str] = Field(None, description="Camera name")
    stream_url: Optional[str] = Field(None, description="Stream URL")
    location_description: Optional[str] = Field(None, description="Location description")
    is_active: Optional[bool] = Field(None, description="Is camera active")


class CameraResponse(BaseModel):
    """Response model for camera information."""
    id: UUID = Field(..., description="Camera ID")
    site_id: UUID = Field(..., description="Site ID")
    name: str = Field(..., description="Camera name")
    stream_url: str = Field(..., description="Stream URL")
    status: str = Field(..., description="Camera status")
    location_description: Optional[str] = Field(None, description="Location description")
    is_active: bool = Field(..., description="Is camera active")
    site_name: Optional[str] = Field(None, description="Site name")

    class Config:
        from_attributes = True
