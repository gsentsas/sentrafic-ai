from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_tables
from app.core.logging import logger
from app.api.routes import api_router
from app.db.seed import seed_database
from app.core.database import SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI lifespan events."""
    # Startup
    logger.info("Starting SEN TRAFIC AI Backend API")
    create_tables()
    logger.info("Database tables created/verified")

    # Optional: seed database with demo data
    try:
        db = SessionLocal()
        seed_database(db)
        db.close()
    except Exception as e:
        logger.warning(f"Database seeding skipped: {e}")

    yield

    # Shutdown
    logger.info("Shutting down SEN TRAFIC AI Backend API")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI backend for computer vision-based traffic analysis platform",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Add CORS middleware (allow all for MVP - restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root health endpoint
@app.get("/health")
def root_health():
    """Root health check endpoint."""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Include API router
app.include_router(api_router)


# Root endpoint
@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "SEN TRAFIC AI Backend API",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
