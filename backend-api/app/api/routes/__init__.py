from fastapi import APIRouter

from app.api.routes import auth, health, sites, cameras, dashboard, analytics, alerts, ingest, exports

api_router = APIRouter(prefix="/api")

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["cameras"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])

__all__ = ["api_router"]
