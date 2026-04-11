from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db
from app.schemas.site import SiteCreate, SiteUpdate, SiteResponse
from app.services.site_service import (
    list_sites,
    get_site,
    create_site,
    update_site,
)

router = APIRouter()


@router.get("/", response_model=list)
def get_sites(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    site_type: str = Query(None),
):
    """
    Get list of all sites.

    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **site_type**: Filter by site type (optional)
    """
    return list_sites(db, skip=skip, limit=limit, site_type=site_type)


@router.post("/", response_model=SiteResponse)
def create_new_site(
    site_create: SiteCreate,
    db: Session = Depends(get_db),
):
    """Create a new site."""
    site = create_site(db, site_create)
    return SiteResponse(
        id=site.id,
        name=site.name,
        slug=site.slug,
        address=site.address,
        city=site.city,
        latitude=site.latitude,
        longitude=site.longitude,
        site_type=site.site_type.value,
        is_active=site.is_active,
        camera_count=len(site.cameras),
    )


@router.get("/{site_id}", response_model=SiteResponse)
def get_site_by_id(
    site_id: UUID,
    db: Session = Depends(get_db),
):
    """Get details of a specific site."""
    return get_site(db, site_id)


@router.put("/{site_id}", response_model=SiteResponse)
def update_site_by_id(
    site_id: UUID,
    site_update: SiteUpdate,
    db: Session = Depends(get_db),
):
    """Update a site."""
    site = update_site(db, site_id, site_update)
    return SiteResponse(
        id=site.id,
        name=site.name,
        slug=site.slug,
        address=site.address,
        city=site.city,
        latitude=site.latitude,
        longitude=site.longitude,
        site_type=site.site_type.value,
        is_active=site.is_active,
        camera_count=len(site.cameras),
    )
