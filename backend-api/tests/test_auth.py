import pytest
from app.core.security import hash_password
from app.models.user import User, UserRole


def test_login_valid_credentials(client, db):
    """Test login with valid credentials."""
    # Create test user
    user = User(
        email="test@sentrafic.sn",
        hashed_password=hash_password("password123"),
        full_name="Test User",
        role=UserRole.viewer,
    )
    db.add(user)
    db.commit()

    # Test login
    response = client.post(
        "/api/auth/login",
        json={"email": "test@sentrafic.sn", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_email(client, db):
    """Test login with invalid email."""
    response = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@sentrafic.sn", "password": "password123"},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_invalid_password(client, db):
    """Test login with invalid password."""
    # Create test user
    user = User(
        email="test@sentrafic.sn",
        hashed_password=hash_password("password123"),
        full_name="Test User",
        role=UserRole.viewer,
    )
    db.add(user)
    db.commit()

    # Test login with wrong password
    response = client.post(
        "/api/auth/login",
        json={"email": "test@sentrafic.sn", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_inactive_user(client, db):
    """Test login with inactive user."""
    # Create inactive user
    user = User(
        email="inactive@sentrafic.sn",
        hashed_password=hash_password("password123"),
        full_name="Inactive User",
        role=UserRole.viewer,
        is_active=False,
    )
    db.add(user)
    db.commit()

    # Test login
    response = client.post(
        "/api/auth/login",
        json={"email": "inactive@sentrafic.sn", "password": "password123"},
    )
    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()
