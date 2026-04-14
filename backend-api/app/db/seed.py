import random
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.models.user import User, UserRole
from app.models.site import Site, SiteType
from app.models.camera import Camera, CameraStatus
from app.models.traffic_aggregate import TrafficAggregate, CongestionLevel
from app.models.alert import Alert, AlertType, AlertSeverity
from app.models.camera_health import CameraHealthCheck, HealthStatus
from app.core.security import hash_password
from app.core.config import settings

random.seed(42)  # Deterministic demo data


def seed_database(db: Session):
    """Seed the database with realistic demo data for Dakar traffic supervision."""
    if db.query(User).count() > 0:
        print("[seed] Base deja peuplee, ignoree.")
        return

    now = datetime.now(timezone.utc)

    # ── Users ──────────────────────────────────────────
    admin = User(
        email=settings.ADMIN_EMAIL,
        hashed_password=hash_password(settings.ADMIN_PASSWORD),
        full_name="Amadou Diallo",
        role=UserRole.admin,
        is_active=True,
    )
    operator = User(
        email="operateur@sentrafic.sn",
        hashed_password=hash_password("operateur123"),
        full_name="Fatou Sow",
        role=UserRole.operator,
        is_active=True,
    )
    viewer = User(
        email="observateur@sentrafic.sn",
        hashed_password=hash_password("observateur123"),
        full_name="Moussa Ndiaye",
        role=UserRole.viewer,
        is_active=True,
    )
    db.add_all([admin, operator, viewer])
    db.flush()

    # ── Sites ──────────────────────────────────────────
    site_malick = Site(
        name="Carrefour Malick Sy",
        slug="carrefour-malick-sy",
        address="Rond-point Malick Sy, Plateau",
        city="Dakar",
        latitude=14.6937,
        longitude=-17.4441,
        site_type=SiteType.intersection,
        is_active=True,
    )
    site_autoroute = Site(
        name="Autoroute a peage Dakar-Diamniadio",
        slug="autoroute-dakar-diamniadio",
        address="Autoroute A1, sortie Pikine",
        city="Dakar",
        latitude=14.7645,
        longitude=-17.3912,
        site_type=SiteType.highway,
        is_active=True,
    )
    site_baux = Site(
        name="Gare Routiere des Baux Maraichers",
        slug="gare-baux-maraichers",
        address="Avenue Cheikh Anta Diop",
        city="Dakar",
        latitude=14.7167,
        longitude=-17.4533,
        site_type=SiteType.bus_station,
        is_active=True,
    )
    site_indus = Site(
        name="Zone Industrielle de Diamniadio",
        slug="zone-industrielle-diamniadio",
        address="Parc Industriel International",
        city="Diamniadio",
        latitude=14.7500,
        longitude=-17.1833,
        site_type=SiteType.industrial,
        is_active=True,
    )
    db.add_all([site_malick, site_autoroute, site_baux, site_indus])
    db.flush()

    # ── Cameras ────────────────────────────────────────
    cams = []

    def _cam(site, name, url, status, desc, last_seen_delta_min=None):
        ls = (now - timedelta(minutes=last_seen_delta_min)) if last_seen_delta_min else None
        c = Camera(
            site_id=site.id, name=name, stream_url=url, status=status,
            location_description=desc, is_active=True, last_seen_at=ls,
        )
        cams.append(c)
        return c

    # Malick Sy – 3 cameras (2 online, 1 error)
    cam_ms_n = _cam(site_malick, "Malick Sy Nord", "rtsp://10.0.1.11/live", CameraStatus.online, "Vue nord du carrefour", 2)
    cam_ms_s = _cam(site_malick, "Malick Sy Sud", "rtsp://10.0.1.12/live", CameraStatus.online, "Vue sud du carrefour", 3)
    cam_ms_e = _cam(site_malick, "Malick Sy Est", "rtsp://10.0.1.13/live", CameraStatus.error, "Vue est, signal intermittent", 45)

    # Autoroute – 2 cameras (1 online, 1 offline)
    cam_ar_15 = _cam(site_autoroute, "Autoroute KM15", "rtsp://10.0.2.21/live", CameraStatus.online, "Point km 15, voie rapide", 1)
    cam_ar_25 = _cam(site_autoroute, "Autoroute KM25", "rtsp://10.0.2.22/live", CameraStatus.offline, "Point km 25, hors ligne depuis 6h", 360)

    # Baux Maraichers – 2 cameras (online)
    cam_bx_e = _cam(site_baux, "Baux Maraichers Entree", "rtsp://10.0.3.31/live", CameraStatus.online, "Entree principale gare routiere", 2)
    cam_bx_q = _cam(site_baux, "Baux Maraichers Quais", "rtsp://10.0.3.32/live", CameraStatus.online, "Zone d'embarquement", 5)

    # Diamniadio – 2 cameras (1 online, 1 offline)
    cam_di_e = _cam(site_indus, "Diamniadio Entree", "rtsp://10.0.4.41/live", CameraStatus.online, "Entree zone industrielle", 8)
    cam_di_p = _cam(site_indus, "Diamniadio Parking PL", "rtsp://10.0.4.42/live", CameraStatus.offline, "Parking poids lourds, camera deconnectee", 720)

    db.add_all(cams)
    db.flush()

    # ── Traffic profiles per site ──────────────────────
    # Realistic 15-min counts: (car, bus, truck, moto, person) base at peak
    PROFILES = {
        cam_ms_n.id: {"peak": (120, 8, 4, 35, 20), "mid": (65, 5, 2, 18, 12), "night": (15, 1, 1, 5, 3), "site_id": site_malick.id},
        cam_ms_s.id: {"peak": (100, 6, 3, 30, 18), "mid": (55, 4, 2, 15, 10), "night": (12, 1, 1, 4, 2), "site_id": site_malick.id},
        cam_ar_15.id: {"peak": (180, 12, 15, 25, 2), "mid": (100, 8, 10, 12, 1), "night": (30, 2, 5, 3, 0), "site_id": site_autoroute.id},
        cam_bx_e.id: {"peak": (40, 25, 5, 20, 45), "mid": (25, 18, 3, 12, 30), "night": (5, 3, 1, 3, 5), "site_id": site_baux.id},
        cam_bx_q.id: {"peak": (15, 30, 2, 10, 60), "mid": (10, 20, 1, 6, 35), "night": (2, 5, 0, 2, 8), "site_id": site_baux.id},
        cam_di_e.id: {"peak": (50, 5, 20, 8, 10), "mid": (30, 3, 12, 5, 6), "night": (5, 0, 3, 1, 1), "site_id": site_indus.id},
    }

    def _get_period(hour):
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            return "peak"
        elif 10 <= hour <= 16:
            return "mid"
        return "night"

    def _congestion(total, period):
        if period == "peak" and total > 150:
            return CongestionLevel.heavy
        if period == "peak" and total > 100:
            return CongestionLevel.moderate
        if total > 200:
            return CongestionLevel.blocked
        if total > 120:
            return CongestionLevel.moderate
        return CongestionLevel.free

    # Generate 48h of traffic data (192 x 15-min slots)
    for slot in range(192):
        ts = now - timedelta(minutes=15 * slot)
        hour = ts.hour
        period = _get_period(hour)

        for cam_id, profile in PROFILES.items():
            base = profile[period]
            # Add realistic variance (+-20%)
            def v(x):
                return max(0, x + random.randint(-int(x * 0.2) - 1, int(x * 0.2) + 1))

            car, bus, truck, moto, person = v(base[0]), v(base[1]), v(base[2]), v(base[3]), v(base[4])
            total = car + bus + truck + moto + person
            occ = min(1.0, total / 250.0)

            agg = TrafficAggregate(
                camera_id=cam_id,
                timestamp=ts,
                period_seconds=900,
                car_count=car,
                bus_count=bus,
                truck_count=truck,
                motorcycle_count=moto,
                person_count=person,
                total_count=total,
                avg_occupancy=round(occ, 3),
                congestion_level=_congestion(total, period),
            )
            db.add(agg)

    db.flush()

    # ── Camera health records ──────────────────────────
    for cam in cams:
        if cam.status == CameraStatus.online:
            h = CameraHealthCheck(
                camera_id=cam.id, status=HealthStatus.ok,
                fps=25.0, latency_ms=45,
                last_frame_at=cam.last_seen_at or now,
                checked_at=now,
            )
        elif cam.status == CameraStatus.error:
            h = CameraHealthCheck(
                camera_id=cam.id, status=HealthStatus.degraded,
                fps=8.0, latency_ms=350,
                last_frame_at=cam.last_seen_at,
                checked_at=now,
            )
        else:
            h = CameraHealthCheck(
                camera_id=cam.id, status=HealthStatus.offline,
                fps=0.0, latency_ms=0,
                last_frame_at=cam.last_seen_at,
                checked_at=now,
            )
        db.add(h)
    db.flush()

    # ── Alerts ─────────────────────────────────────────
    alerts_data = [
        # Open alerts
        (cam_ms_n.id, site_malick.id, AlertType.congestion, AlertSeverity.warning,
         "Circulation dense detectee au carrefour Malick Sy Nord — 185 vehicules/15min", False, None),
        (cam_ms_e.id, site_malick.id, AlertType.camera_offline, AlertSeverity.critical,
         "Camera Malick Sy Est : signal intermittent, derniere image il y a 45 min", False, None),
        (cam_ar_25.id, site_autoroute.id, AlertType.camera_offline, AlertSeverity.critical,
         "Camera Autoroute KM25 hors ligne depuis 6 heures", False, None),
        (cam_di_p.id, site_indus.id, AlertType.no_recent_data, AlertSeverity.warning,
         "Aucune donnee recue de Diamniadio Parking PL depuis 12 heures", False, None),
        (cam_ms_s.id, site_malick.id, AlertType.stopped_vehicle, AlertSeverity.info,
         "Vehicule potentiellement immobilise detecte voie sud Malick Sy", False, None),
        (cam_bx_e.id, site_baux.id, AlertType.abnormal_high_traffic, AlertSeverity.warning,
         "Trafic anormalement eleve a l'entree des Baux Maraichers — +40% vs moyenne", False, None),
        # Resolved alerts
        (cam_ar_15.id, site_autoroute.id, AlertType.congestion, AlertSeverity.critical,
         "Congestion majeure sur autoroute KM15 — resolue apres intervention", True, now - timedelta(hours=3)),
        (cam_ms_n.id, site_malick.id, AlertType.congestion, AlertSeverity.warning,
         "Congestion moderee matinale au carrefour Malick Sy — resorbee naturellement", True, now - timedelta(hours=8)),
        (cam_bx_q.id, site_baux.id, AlertType.stopped_vehicle, AlertSeverity.info,
         "Vehicule immobilise sur quai 3 — deplace par le conducteur", True, now - timedelta(hours=5)),
        (cam_di_e.id, site_indus.id, AlertType.abnormal_low_traffic, AlertSeverity.info,
         "Trafic anormalement faible a Diamniadio — jour ferie confirme", True, now - timedelta(hours=12)),
    ]

    for cam_id, site_id, atype, sev, msg, resolved, resolved_at in alerts_data:
        alert = Alert(
            camera_id=cam_id, site_id=site_id,
            alert_type=atype, severity=sev, message=msg,
            is_resolved=resolved,
            resolved_at=resolved_at,
            resolved_by=admin.id if resolved else None,
            created_at=now - timedelta(hours=random.randint(1, 24)),
        )
        db.add(alert)

    db.commit()
    print("[seed] Base de donnees peuplee avec succes — 4 sites, 9 cameras, ~1150 aggregats, 10 alertes.")
