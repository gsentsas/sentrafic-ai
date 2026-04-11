from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class SiteCreate(BaseModel):
    """Request model for creating a site."""
    name: str = Field(..., description="Site name")
    address: str = Field(..., description="Site address")
    city: str = Field(..., description="City")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    site_type: str = Field(default="intersection", description="Type of site")


class SiteUpdate(BaseModel):
    """Request model for updating a site."""
    name: Optional[str] = Field(None, description="Site name")
    address: Optional[str] = Field(None, description="Site address")
    city: Optional[str] = Field(None, description="City")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    site_type: Optional[str] = Field(None, description="Type of site")
    is_active: Optional[bool] = Field(None, description="Is site active")


class SiteResponse(BaseModel):
    """Response model for site information."""
    id: UUID = Field(..., description="Site ID")
    name: str = Field(..., description="Site name")
    slug: str = Field(..., description="Site slug")
    address: str = Field(..., description="Site address")
    city: str = Field(..., description="City")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    site_type: str = Field(..., description="Type of site")
    is_active: bool = Field(..., description="Is site active")
    camera_count: int = Field(default=0, description="Number of cameras")

    class Config:
        from_attributes = True
