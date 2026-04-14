from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class AlertType(str, enum.Enum):
    congestion = "congestion"
    stopped_vehicle = "stopped_vehicle"
    camera_offline = "camera_offline"
    no_recent_data = "no_recent_data"
    abnormal_low_traffic = "abnormal_low_traffic"
    abnormal_high_traffic = "abnormal_high_traffic"
    zone_overflow = "zone_overflow"


class AlertSeverity(str, enum.Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


ALERT_DESCRIPTIONS = {
    "congestion": {
        "label": "Congestion detectee",
        "action": "Verifier les conditions de circulation sur le site concerne",
    },
    "stopped_vehicle": {
        "label": "Vehicule immobilise",
        "action": "Verifier la presence d'un vehicule arrete sur la voie",
    },
    "camera_offline": {
        "label": "Camera hors ligne",
        "action": "Verifier la connexion reseau et l'alimentation de la camera",
    },
    "no_recent_data": {
        "label": "Donnees absentes",
        "action": "Verifier le moteur de vision et la remontee des evenements",
    },
    "abnormal_low_traffic": {
        "label": "Trafic anormalement faible",
        "action": "Verifier si un evenement perturbe la circulation",
    },
    "abnormal_high_traffic": {
        "label": "Trafic anormalement eleve",
        "action": "Surveiller la situation et anticiper une congestion",
    },
    "zone_overflow": {
        "label": "Zone saturee",
        "action": "Envisager une regulation du flux entrant",
    },
}


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False, default=AlertSeverity.warning)
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False, index=True)
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    camera = relationship("Camera", back_populates="alerts")
    site = relationship("Site", back_populates="alerts")

    @property
    def short_description(self) -> str:
        info = ALERT_DESCRIPTIONS.get(self.alert_type.value if isinstance(self.alert_type, AlertType) else self.alert_type, {})
        return info.get("label", self.alert_type)

    @property
    def recommended_action(self) -> str:
        info = ALERT_DESCRIPTIONS.get(self.alert_type.value if isinstance(self.alert_type, AlertType) else self.alert_type, {})
        return info.get("action", "")

    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.alert_type}, severity={self.severity})>"
