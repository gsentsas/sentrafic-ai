from fastapi import APIRouter, Depends

from app.api.routes import auth, health, sites, cameras, dashboard, analytics, alerts, ingest, exports, users
from app.api.deps import get_current_user

api_router = APIRouter(prefix="/api")

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(
    sites.router,
    prefix="/sites",
    tags=["sites"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    cameras.router,
    prefix="/cameras",
    tags=["cameras"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    alerts.router,
    prefix="/alerts",
    tags=["alerts"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_router.include_router(
    exports.router,
    prefix="/exports",
    tags=["exports"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(users.router, prefix="/users", tags=["users"])

__all__ = ["api_router"]
