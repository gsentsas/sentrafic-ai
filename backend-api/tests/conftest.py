import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base
from app.core.config import settings
from app.db.seed import seed_database

# ── SQLite compatibility patches ──────────────────────────────────────────────
# PostgreSQL UUID type → CHAR(36) in SQLite
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler  # noqa: E402

if not hasattr(SQLiteTypeCompiler, "visit_UUID"):
    SQLiteTypeCompiler.visit_UUID = lambda self, type_, **kw: "CHAR(36)"

# Use SQLite in-memory for tests (fast, isolated)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    """Get a database session for tests (rolled back after each test)."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    def override_get_db():
        yield session

    # Override both the canonical get_db (used by security.py via DI)
    # and the re-export in deps.py (same object, but explicit for clarity)
    from app.core.database import get_db
    app.dependency_overrides[get_db] = override_get_db

    yield session

    session.close()
    transaction.rollback()
    connection.close()
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(db):
    """Standard test client (no auth, no API key)."""
    return TestClient(app)


@pytest.fixture(scope="function")
def ingest_client(db):
    """Test client pre-configured with the vision-engine API key."""
    return TestClient(app, headers={"X-API-Key": settings.VISION_API_KEY})


@pytest.fixture(scope="function")
def admin_client(db):
    """Test client authenticated as admin (uses JWT from login)."""
    from app.models.user import User, UserRole
    from app.core.security import hash_password

    # Create admin user
    admin = User(
        email="admin_test@sentrafic.sn",
        hashed_password=hash_password("adminpass123"),
        full_name="Admin Test",
        role=UserRole.admin,
        is_active=True,
    )
    db.add(admin)
    db.commit()

    # Login to get token
    c = TestClient(app)
    resp = c.post("/api/auth/login", json={"email": "admin_test@sentrafic.sn", "password": "adminpass123"})
    token = resp.json()["access_token"]
    return TestClient(app, headers={"Authorization": f"Bearer {token}"})


@pytest.fixture(scope="function")
def setup_test_data(db):
    """Seed full demo data in the test DB."""
    seed_database(db)
    return db
