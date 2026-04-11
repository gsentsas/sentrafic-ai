from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Dict


class TrafficAggregateResponse(BaseModel):
    """Response model for traffic aggregate data."""
    id: UUID = Field(..., description="Aggregate ID")
    camera_id: UUID = Field(..., description="Camera ID")
    timestamp: datetime = Field(..., description="Timestamp of the aggregate")
    period_seconds: int = Field(..., description="Aggregation period in seconds")
    car_count: int = Field(..., description="Number of cars detected")
    bus_count: int = Field(..., description="Number of buses detected")
    truck_count: int = Field(..., description="Number of trucks detected")
    motorcycle_count: int = Field(..., description="Number of motorcycles detected")
    person_count: int = Field(..., description="Number of people detected")
    total_count: int = Field(..., description="Total count")
    avg_occupancy: float = Field(..., description="Average occupancy (0-1)")
    congestion_level: str = Field(..., description="Congestion level")

    class Config:
        from_attributes = True


class ClassCount(BaseModel):
    """Model for class count."""
    car: int = Field(default=0, description="Car count")
    bus: int = Field(default=0, description="Bus count")
    truck: int = Field(default=0, description="Truck count")
    motorcycle: int = Field(default=0, description="Motorcycle count")
    person: int = Field(default=0, description="Person count")


class TrafficSummary(BaseModel):
    """Summary model for traffic data."""
    total_vehicles: int = Field(..., description="Total vehicle count")
    by_class: ClassCount = Field(..., description="Count by vehicle class")
    period_start: datetime = Field(..., description="Period start time")
    period_end: datetime = Field(..., description="Period end time")
    avg_congestion_level: str = Field(..., description="Average congestion level")


class TrafficTrendPoint(BaseModel):
    """Single point in a traffic trend."""
    timestamp: datetime = Field(..., description="Timestamp")
    total_count: int = Field(..., description="Total count at this timestamp")
    car_count: int = Field(default=0, description="Car count")
    congestion_level: str = Field(..., description="Congestion level")


class TrafficTrend(BaseModel):
    """Trend model for traffic data over time."""
    camera_id: UUID = Field(..., description="Camera ID")
    period: str = Field(..., description="Trend period")
    points: List[TrafficTrendPoint] = Field(..., description="Trend data points")
