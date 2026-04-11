from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import uuid

from app.models.user import User, UserRole
from app.models.site import Site, SiteType
from app.models.camera import Camera, CameraStatus
from app.models.traffic_aggregate import TrafficAggregate, CongestionLevel
from app.models.alert import Alert, AlertType, AlertSeverity
from app.core.security import hash_password
from app.core.config import settings


def seed_database(db: Session):
    """Seed the database with demo data."""
    # Check if data already exists
    if db.query(User).count() > 0:
        print("Database already seeded, skipping...")
        return

    # Create admin user
    admin_user = User(
        email=settings.ADMIN_EMAIL,
        hashed_password=hash_password(settings.ADMIN_PASSWORD),
        full_name="Admin User",
        role=UserRole.admin,
        is_active=True,
    )
    db.add(admin_user)
    db.flush()

    # Create demo users
    operator_user = User(
        email="operator@sentrafic.sn",
        hashed_password=hash_password("operator123"),
        full_name="Traffic Operator",
        role=UserRole.operator,
        is_active=True,
    )
    viewer_user = User(
        email="viewer@sentrafic.sn",
        hashed_password=hash_password("viewer123"),
        full_name="Traffic Viewer",
        role=UserRole.viewer,
        is_active=True,
    )
    db.add(operator_user)
    db.add(viewer_user)
    db.flush()

    # Create demo sites
    site1 = Site(
        name="Carrefour Malick Sy",
        slug="carrefour-malick-sy",
        address="Rond-point Malick Sy",
        city="Dakar",
        latitude=14.7167,
        longitude=-17.4667,
        site_type=SiteType.intersection,
        is_active=True,
    )
    site2 = Site(
        name="Autoroute Dakar-Diamniadio",
        slug="autoroute-dakar-diamniadio",
        address="Autoroute A1",
        city="Dakar",
        latitude=14.8,
        longitude=-17.4,
        site_type=SiteType.highway,
        is_active=True,
    )
    site3 = Site(
        name="Gare Routière Pompiers",
        slug="gare-routiere-pompiers",
        address="Boulevard de la République",
        city="Dakar",
        latitude=14.6667,
        longitude=-17.4333,
        site_type=SiteType.bus_station,
        is_active=True,
    )
    db.add(site1)
    db.add(site2)
    db.add(site3)
    db.flush()

    # Create demo cameras
    cameras = [
        Camera(
            site_id=site1.id,
            name="Malick Sy North",
            stream_url="rtsp://camera1.example.com/stream",
            location_description="Intersection north side",
            status=CameraStatus.online,
            is_active=True,
        ),
        Camera(
            site_id=site1.id,
            name="Malick Sy South",
            stream_url="rtsp://camera2.example.com/stream",
            location_description="Intersection south side",
            status=CameraStatus.online,
            is_active=True,
        ),
        Camera(
            site_id=site2.id,
            name="Highway KM15",
            stream_url="rtsp://camera3.example.com/stream",
            location_description="Highway kilometer 15",
            status=CameraStatus.online,
            is_active=True,
        ),
        Camera(
            site_id=site2.id,
            name="Highway KM25",
            stream_url="rtsp://camera4.example.com/stream",
            location_description="Highway kilometer 25",
            status=CameraStatus.offline,
            is_active=True,
        ),
        Camera(
            site_id=site3.id,
            name="Bus Station Main Entrance",
            stream_url="rtsp://camera5.example.com/stream",
            location_description="Main entrance",
            status=CameraStatus.online,
            is_active=True,
        ),
    ]
    for camera in cameras:
        db.add(camera)
    db.flush()

    # Create sample traffic aggregates for last 24 hours
    now = datetime.now(timezone.utc)
    for i in range(96):  # 96 records = 24 hours * 4 (15-min periods)
        timestamp = now - timedelta(minutes=15 * i)

        for camera in cameras:
            if camera.status == CameraStatus.offline:
                continue

            # Vary traffic based on time of day
            hour = timestamp.hour
            if 7 <= hour <= 9 or 17 <= hour <= 19:
                # Peak hours
                base_cars = 150
                base_motorcycles = 30
                congestion = CongestionLevel.moderate
            elif 10 <= hour <= 16:
                # Mid-day
                base_cars = 80
                base_motorcycles = 15
                congestion = CongestionLevel.free
            else:
                # Night hours
                base_cars = 20
                base_motorcycles = 5
                congestion = CongestionLevel.free

            # Add some randomness
            import random
            car_count = max(10, base_cars + random.randint(-20, 30))
            bus_count = random.randint(2, 8)
            truck_count = random.randint(1, 5)
            motorcycle_count = max(3, base_motorcycles + random.randint(-10, 15))
            person_count = random.randint(5, 25)

            total = car_count + bus_count + truck_count + motorcycle_count + person_count

            aggregate = TrafficAggregate(
                camera_id=camera.id,
                timestamp=timestamp,
                period_seconds=900,
                car_count=car_count,
                bus_count=bus_count,
                truck_count=truck_count,
                motorcycle_count=motorcycle_count,
                person_count=person_count,
                total_count=total,
                avg_occupancy=min(1.0, total / 200.0),
                congestion_level=congestion,
            )
            db.add(aggregate)

    db.flush()

    # Create sample alerts
    alert1 = Alert(
        camera_id=cameras[1].id,
        site_id=site1.id,
        alert_type=AlertType.congestion,
        severity=AlertSeverity.warning,
        message="Moderate traffic congestion detected at Malick Sy South",
        is_resolved=False,
    )
    alert2 = Alert(
        camera_id=cameras[3].id,
        site_id=site2.id,
        alert_type=AlertType.camera_offline,
        severity=AlertSeverity.critical,
        message="Camera at Highway KM25 is offline",
        is_resolved=False,
    )
    alert3 = Alert(
        camera_id=cameras[0].id,
        site_id=site1.id,
        alert_type=AlertType.congestion,
        severity=AlertSeverity.critical,
        message="Heavy traffic congestion at Malick Sy North",
        is_resolved=True,
        resolved_at=now - timedelta(hours=2),
        resolved_by=admin_user.id,
    )
    db.add(alert1)
    db.add(alert2)
    db.add(alert3)

    db.commit()
    print("Database seeded successfully!")
