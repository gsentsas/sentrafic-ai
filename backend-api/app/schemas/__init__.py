from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.schemas.site import SiteCreate, SiteUpdate, SiteResponse
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse
from app.schemas.traffic import TrafficAggregateResponse, TrafficSummary, TrafficTrend
from app.schemas.alert import AlertResponse, AlertResolve
from app.schemas.ingest import IngestEvent, IngestBatch, IngestResponse

__all__ = [
    "LoginRequest",
    "TokenResponse",
    "UserResponse",
    "SiteCreate",
    "SiteUpdate",
    "SiteResponse",
    "CameraCreate",
    "CameraUpdate",
    "CameraResponse",
    "TrafficAggregateResponse",
    "TrafficSummary",
    "TrafficTrend",
    "AlertResponse",
    "AlertResolve",
    "IngestEvent",
    "IngestBatch",
    "IngestResponse",
]
