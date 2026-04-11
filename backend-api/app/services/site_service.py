from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from uuid import UUID
import re

from app.models.site import Site, SiteType
from app.schemas.site import SiteCreate, SiteUpdate


def _generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from a name."""
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def list_sites(db: Session, skip: int = 0, limit: int = 100, site_type: str = None):
    """List all sites with optional filtering."""
    query = db.query(Site)

    if site_type:
        query = query.filter(Site.site_type == site_type)

    sites = query.offset(skip).limit(limit).all()

    # Add camera counts
    result = []
    for site in sites:
        site_dict = {
            "id": site.id,
            "name": site.name,
            "slug": site.slug,
            "address": site.address,
            "city": site.city,
            "latitude": site.latitude,
            "longitude": site.longitude,
            "site_type": site.site_type.value,
            "is_active": site.is_active,
            "camera_count": len(site.cameras),
        }
        result.append(site_dict)

    return result


def get_site(db: Session, site_id: UUID):
    """Get a site by ID."""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    return {
        "id": site.id,
        "name": site.name,
        "slug": site.slug,
        "address": site.address,
        "city": site.city,
        "latitude": site.latitude,
        "longitude": site.longitude,
        "site_type": site.site_type.value,
        "is_active": site.is_active,
        "camera_count": len(site.cameras),
    }


def create_site(db: Session, site_create: SiteCreate) -> Site:
    """Create a new site."""
    slug = _generate_slug(site_create.name)

    # Check if slug already exists
    existing = db.query(Site).filter(Site.slug == slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Site with this name already exists",
        )

    site = Site(
        name=site_create.name,
        slug=slug,
        address=site_create.address,
        city=site_create.city,
        latitude=site_create.latitude,
        longitude=site_create.longitude,
        site_type=SiteType(site_create.site_type),
    )

    db.add(site)
    db.commit()
    db.refresh(site)
    return site


def update_site(db: Session, site_id: UUID, site_update: SiteUpdate) -> Site:
    """Update a site."""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    update_data = site_update.model_dump(exclude_unset=True)

    # If name is being updated, regenerate slug
    if "name" in update_data:
        new_slug = _generate_slug(update_data["name"])
        existing = db.query(Site).filter(
            Site.slug == new_slug,
            Site.id != site_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Site with this name already exists",
            )
        update_data["slug"] = new_slug

    # Convert site_type to enum if provided
    if "site_type" in update_data:
        update_data["site_type"] = SiteType(update_data["site_type"])

    for field, value in update_data.items():
        setattr(site, field, value)

    db.add(site)
    db.commit()
    db.refresh(site)
    return site


def get_site_count(db: Session) -> int:
    """Get total count of sites."""
    return db.query(func.count(Site.id)).scalar() or 0
