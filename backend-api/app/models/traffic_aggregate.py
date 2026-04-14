from sqlalchemy import Column, Integer, Float, DateTime, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class CongestionLevel(str, enum.Enum):
    """Congestion level enumeration."""
    free = "free"
    moderate = "moderate"
    heavy = "heavy"
    blocked = "blocked"


class TrafficAggregate(Base):
    """Traffic aggregate model for storing aggregated detection counts."""
    __tablename__ = "traffic_aggregates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    period_seconds = Column(Integer, nullable=False)  # Aggregation period (e.g., 300 for 5 minutes)

    # Vehicle/pedestrian counts by class
    car_count = Column(Integer, default=0)
    bus_count = Column(Integer, default=0)
    truck_count = Column(Integer, default=0)
    motorcycle_count = Column(Integer, default=0)
    person_count = Column(Integer, default=0)

    # Aggregate values
    total_count = Column(Integer, default=0)
    avg_occupancy = Column(Float, default=0.0)  # 0-1
    congestion_level = Column(Enum(CongestionLevel), nullable=False, default=CongestionLevel.free)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    camera = relationship("Camera", back_populates="traffic_aggregates")

    def __repr__(self):
        return f"<TrafficAggregate(id={self.id}, timestamp={self.timestamp}, total_count={self.total_count})>"
