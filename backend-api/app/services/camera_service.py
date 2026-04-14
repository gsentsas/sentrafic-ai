from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from uuid import UUID

from app.models.camera import Camera, CameraStatus
from app.models.site import Site
from app.schemas.camera import CameraCreate, CameraUpdate


def _serialize_camera(camera: Camera, site: Site = None) -> dict:
    return {
        "id": camera.id,
        "site_id": camera.site_id,
        "name": camera.name,
        "stream_url": camera.stream_url,
        "status": camera.status.value,
        "location_description": camera.location_description,
        "is_active": camera.is_active,
        "last_seen_at": camera.last_seen_at.isoformat() if camera.last_seen_at else None,
        "health_label": camera.health_label,
        "created_at": camera.created_at.isoformat() if camera.created_at else None,
        "site_name": site.name if site else None,
    }


def list_cameras(db: Session, site_id: UUID = None, skip: int = 0, limit: int = 100):
    query = db.query(Camera).filter(Camera.is_active == True)
    if site_id:
        query = query.filter(Camera.site_id == site_id)
    cameras = query.offset(skip).limit(limit).all()
    result = []
    for camera in cameras:
        site = db.query(Site).filter(Site.id == camera.site_id).first()
        result.append(_serialize_camera(camera, site))
    return result


def get_camera(db: Session, camera_id: UUID):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera introuvable")
    site = db.query(Site).filter(Site.id == camera.site_id).first()
    return _serialize_camera(camera, site)


def create_camera(db: Session, camera_create: CameraCreate) -> Camera:
    site = db.query(Site).filter(Site.id == camera_create.site_id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site introuvable")
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
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera introuvable")
    update_data = camera_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(camera, field, value)
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


def update_camera_status(db: Session, camera_id: UUID, new_status: str) -> Camera:
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera introuvable")
    camera.status = CameraStatus(new_status)
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


def get_camera_count(db: Session, is_online: bool = None) -> int:
    query = db.query(func.count(Camera.id)).filter(Camera.is_active == True)
    if is_online is True:
        query = query.filter(Camera.status == CameraStatus.online)
    elif is_online is False:
        query = query.filter(Camera.status != CameraStatus.online)
    return query.scalar() or 0


def get_cameras_by_site(db: Session, site_id: UUID):
    return db.query(Camera).filter(Camera.site_id == site_id).all()
