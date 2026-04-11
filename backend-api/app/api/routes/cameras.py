from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse
from app.services.camera_service import (
    list_cameras,
    get_camera,
    create_camera,
    update_camera,
)
from app.models.camera import Camera
from app.models.site import Site

router = APIRouter()


@router.get("/", response_model=list)
def get_cameras(
    db: Session = Depends(get_db),
    site_id: UUID = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get list of cameras.

    - **site_id**: Filter by site ID (optional)
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    return list_cameras(db, site_id=site_id, skip=skip, limit=limit)


@router.post("/", response_model=CameraResponse)
def create_new_camera(
    camera_create: CameraCreate,
    db: Session = Depends(get_db),
):
    """Create a new camera."""
    camera = create_camera(db, camera_create)
    site = db.query(Site).filter(Site.id == camera.site_id).first()
    return CameraResponse(
        id=camera.id,
        site_id=camera.site_id,
        name=camera.name,
        stream_url=camera.stream_url,
        status=camera.status.value,
        location_description=camera.location_description,
        is_active=camera.is_active,
        site_name=site.name if site else None,
    )


@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera_by_id(
    camera_id: UUID,
    db: Session = Depends(get_db),
):
    """Get details of a specific camera."""
    return get_camera(db, camera_id)


@router.put("/{camera_id}", response_model=CameraResponse)
def update_camera_by_id(
    camera_id: UUID,
    camera_update: CameraUpdate,
    db: Session = Depends(get_db),
):
    """Update a camera."""
    camera = update_camera(db, camera_id, camera_update)
    site = db.query(Site).filter(Site.id == camera.site_id).first()
    return CameraResponse(
        id=camera.id,
        site_id=camera.site_id,
        name=camera.name,
        stream_url=camera.stream_url,
        status=camera.status.value,
        location_description=camera.location_description,
        is_active=camera.is_active,
        site_name=site.name if site else None,
    )
