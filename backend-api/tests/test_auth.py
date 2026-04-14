import pytest
from app.core.security import hash_password
from app.models.user import User, UserRole


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _make_user(db, email="test@sentrafic.sn", password="password123",
               role=UserRole.viewer, active=True):
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name="Test User",
        role=role,
        is_active=active,
    )
    db.add(user)
    db.commit()
    return user


def _login(client, email, password):
    return client.post("/api/auth/login", json={"email": email, "password": password})


# ──────────────────────────────────────────────────────────────────────────────
# Login
# ──────────────────────────────────────────────────────────────────────────────

def test_login_valid_credentials(client, db):
    """Login avec identifiants valides → token JWT retourné."""
    _make_user(db)
    response = _login(client, "test@sentrafic.sn", "password123")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20


def test_login_invalid_email(client, db):
    """Email inconnu → 401."""
    response = _login(client, "nobody@sentrafic.sn", "password123")
    assert response.status_code == 401


def test_login_invalid_password(client, db):
    """Mauvais mot de passe → 401."""
    _make_user(db)
    response = _login(client, "test@sentrafic.sn", "wrongpassword")
    assert response.status_code == 401


def test_login_inactive_user(client, db):
    """Utilisateur inactif → 403."""
    _make_user(db, active=False)
    response = _login(client, "test@sentrafic.sn", "password123")
    assert response.status_code == 403


# ──────────────────────────────────────────────────────────────────────────────
# /api/users/me
# ──────────────────────────────────────────────────────────────────────────────

def test_get_me_authenticated(client, db):
    """GET /api/users/me retourne le profil de l'utilisateur connecté."""
    _make_user(db, "me@sentrafic.sn")
    token = _login(client, "me@sentrafic.sn", "password123").json()["access_token"]

    response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@sentrafic.sn"
    assert "role" in data
    assert "is_active" in data


def test_get_me_unauthenticated(client, db):
    """GET /api/users/me sans token → 401."""
    response = client.get("/api/users/me")
    assert response.status_code == 401


# ──────────────────────────────────────────────────────────────────────────────
# Gestion des utilisateurs (admin)
# ──────────────────────────────────────────────────────────────────────────────

def test_list_users_as_admin(admin_client, db):
    """Admin peut lister tous les utilisateurs."""
    response = admin_client.get("/api/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_users_forbidden_for_viewer(client, db):
    """Viewer ne peut pas lister les utilisateurs."""
    _make_user(db, "viewer@sentrafic.sn")
    token = _login(client, "viewer@sentrafic.sn", "password123").json()["access_token"]

    response = client.get("/api/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_create_user_as_admin(admin_client, db):
    """Admin peut créer un utilisateur."""
    response = admin_client.post("/api/users/", json={
        "email": "nouveau@sentrafic.sn",
        "password": "secure123",
        "full_name": "Nouveau User",
        "role": "operator",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "nouveau@sentrafic.sn"
    assert data["role"] == "operator"


def test_create_user_duplicate_email(admin_client, db):
    """Créer un utilisateur avec un email existant → 400."""
    _make_user(db, "dupe@sentrafic.sn")
    response = admin_client.post("/api/users/", json={
        "email": "dupe@sentrafic.sn",
        "password": "secure123",
    })
    assert response.status_code == 400


def test_change_password(client, db):
    """Changer son mot de passe avec l'ancien correct → 200."""
    _make_user(db, "changepass@sentrafic.sn")
    token = _login(client, "changepass@sentrafic.sn", "password123").json()["access_token"]

    response = client.put(
        "/api/users/me/password",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": "password123", "new_password": "newpass456"},
    )
    assert response.status_code == 200

    # L'ancien mot de passe ne fonctionne plus
    assert _login(client, "changepass@sentrafic.sn", "password123").status_code == 401
    # Le nouveau fonctionne
    assert _login(client, "changepass@sentrafic.sn", "newpass456").status_code == 200


def test_change_password_wrong_current(client, db):
    """Mauvais mot de passe actuel → 400."""
    _make_user(db, "badpass@sentrafic.sn")
    token = _login(client, "badpass@sentrafic.sn", "password123").json()["access_token"]

    response = client.put(
        "/api/users/me/password",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": "wrongcurrent", "new_password": "newpass456"},
    )
    assert response.status_code == 400
