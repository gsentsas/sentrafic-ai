from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from uuid import UUID

from app.models.camera import Camera, CameraStatus
from app.models.site import Site
from app.schemas.camera import CameraCreate, CameraUpdate


def list_cameras(db: Session, site_id: UUID = None, skip: int = 0, limit: int = 100):
    """List cameras with optional filtering by site."""
    query = db.query(Camera)

    if site_id:
        query = query.filter(Camera.site_id == site_id)

    cameras = query.offset(skip).limit(limit).all()

    result = []
    for camera in cameras:
        site = db.query(Site).filter(Site.id == camera.site_id).first()
        result.append({
            "id": camera.id,
            "site_id": camera.site_id,
            "name": camera.name,
            "stream_url": camera.stream_url,
            "status": camera.status.value,
            "location_description": camera.location_description,
            "is_active": camera.is_active,
            "site_name": site.name if site else None,
        })

    return result


def get_camera(db: Session, camera_id: UUID):
    """Get a camera by ID."""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    site = db.query(Site).filter(Site.id == camera.site_id).first()
    return {
        "id": camera.id,
        "site_id": camera.site_id,
        "name": camera.name,
        "stream_url": camera.stream_url,
        "status": camera.status.value,
        "location_description": camera.location_description,
        "is_active": camera.is_active,
        "site_name": site.name if site else None,
    }


def create_camera(db: Session, camera_create: CameraCreate) -> Camera:
    """Create a new camera."""
    # Verify site exists
    site = db.query(Site).filter(Site.id == camera_create.site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    camera = Camera(
        site_id=camera_create.site_id,
        name=camera_create.name,
        stream_url=camera_create.stream_url,
        location_description=camera_create.location_description,
        status=CameraStatus.offline,
    )

    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


def update_camera(db: Session, camera_id: UUID, camera_update: CameraUpdate) -> Camera:
    """Update a camera."""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    update_data = camera_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(camera, field, value)

    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


def update_camera_status(
    db: Session,
    camera_id: UUID,
    status: str
) -> Camera:
    """Update camera status."""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    camera.status = CameraStatus(status)
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


def get_camera_count(db: Session, is_online: bool = None) -> int:
    """Get total count of cameras."""
    query = db.query(func.count(Camera.id))

    if is_online is not None:
        status = CameraStatus.online if is_online else CameraStatus.offline
        query = query.filter(Camera.status == status)

    return query.scalar() or 0


def get_cameras_by_site(db: Session, site_id: UUID):
    """Get all cameras for a site."""
    return db.query(Camera).filter(Camera.site_id == site_id).all()
