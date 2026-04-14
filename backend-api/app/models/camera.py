from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class CameraStatus(str, enum.Enum):
    online = "online"
    offline = "offline"
    error = "error"


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    stream_url = Column(String(1024), nullable=False)
    status = Column(Enum(CameraStatus), nullable=False, default=CameraStatus.offline)
    location_description = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    site = relationship("Site", back_populates="cameras")
    traffic_aggregates = relationship("TrafficAggregate", back_populates="camera", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="camera", cascade="all, delete-orphan")
    health_checks = relationship("CameraHealthCheck", back_populates="camera", cascade="all, delete-orphan")

    @property
    def health_label(self) -> str:
        """Compute health label from last_seen_at freshness."""
        if not self.last_seen_at:
            return "unknown"
        from datetime import timezone
        delta = (datetime.now(timezone.utc) - self.last_seen_at).total_seconds()
        if delta < 600:  # < 10 min
            return "healthy"
        elif delta < 1800:  # < 30 min
            return "delayed"
        return "offline"

    def __repr__(self):
        return f"<Camera(id={self.id}, name={self.name}, status={self.status})>"
