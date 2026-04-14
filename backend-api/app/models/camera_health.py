from sqlalchemy import Column, Float, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class HealthStatus(str, enum.Enum):
    """Camera health status enumeration."""
    ok = "ok"
    degraded = "degraded"
    offline = "offline"


class CameraHealthCheck(Base):
    """Camera health check model for monitoring stream quality."""
    __tablename__ = "camera_health_checks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Enum(HealthStatus), nullable=False, default=HealthStatus.offline)
    fps = Column(Float)  # Frames per second
    latency_ms = Column(Integer)  # Latency in milliseconds
    last_frame_at = Column(DateTime(timezone=True))
    checked_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    camera = relationship("Camera", back_populates="health_checks")

    def __repr__(self):
        return f"<CameraHealthCheck(id={self.id}, camera_id={self.camera_id}, status={self.status})>"
