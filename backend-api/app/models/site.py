from sqlalchemy import Column, String, Boolean, DateTime, Enum, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class SiteType(str, enum.Enum):
    """Site type enumeration."""
    intersection = "intersection"
    highway = "highway"
    parking = "parking"
    logistics = "logistics"
    bus_station = "bus_station"
    industrial = "industrial"


class Site(Base):
    """Site model representing a location with traffic cameras."""
    __tablename__ = "sites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    address = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    site_type = Column(Enum(SiteType), nullable=False, default=SiteType.intersection)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    cameras = relationship("Camera", back_populates="site", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="site", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Site(id={self.id}, name={self.name}, city={self.city})>"
