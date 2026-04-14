import pytest
from app.models.site import Site, SiteType


def test_list_sites(admin_client, db):
    """Test listing sites."""
    # Create test site
    site = Site(
        name="Test Site",
        slug="test-site",
        address="123 Test Street",
        city="Dakar",
        latitude=14.7167,
        longitude=-17.4667,
        site_type=SiteType.intersection,
    )
    db.add(site)
    db.commit()

    # Test list endpoint
    response = admin_client.get("/api/sites/")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["name"] == "Test Site"


def test_create_site(admin_client, db):
    """Test creating a site."""
    response = admin_client.post(
        "/api/sites/",
        json={
            "name": "New Site",
            "address": "456 New Street",
            "city": "Thiès",
            "latitude": 14.8,
            "longitude": -16.9,
            "site_type": "intersection",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Site"
    assert data["city"] == "Thiès"
    assert data["slug"] == "new-site"
    assert data["camera_count"] == 0


def test_get_site(admin_client, db):
    """Test getting a specific site."""
    # Create test site
    site = Site(
        name="Get Test Site",
        slug="get-test-site",
        address="789 Get Street",
        city="Dakar",
        latitude=14.7,
        longitude=-17.5,
        site_type=SiteType.highway,
    )
    db.add(site)
    db.commit()

    # Test get endpoint
    response = admin_client.get(f"/api/sites/{site.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Get Test Site"
    assert data["city"] == "Dakar"


def test_update_site(admin_client, db):
    """Test updating a site."""
    # Create test site
    site = Site(
        name="Update Test Site",
        slug="update-test-site",
        address="999 Update Street",
        city="Dakar",
        latitude=14.7,
        longitude=-17.5,
        site_type=SiteType.parking,
    )
    db.add(site)
    db.commit()

    # Test update endpoint
    response = admin_client.put(
        f"/api/sites/{site.id}",
        json={
            "name": "Updated Site Name",
            "city": "Saint-Louis",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Site Name"
    assert data["city"] == "Saint-Louis"


def test_get_nonexistent_site(admin_client):
    """Test getting a non-existent site."""
    import uuid
    response = admin_client.get(f"/api/sites/{uuid.uuid4()}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
