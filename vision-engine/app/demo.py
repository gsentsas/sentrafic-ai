"""
Demo/simulation mode for the vision engine.

Generates realistic synthetic traffic data without requiring a real camera
or YOLO model. Simulates Dakar traffic patterns with peak hours, weekday
variance, and random congestion events.

Activated when VISION_DEMO_MODE=true (default in docker-compose).
"""

import signal
import sys
import time
import random
import math
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

import requests

from app.utils import setup_logger

logger = setup_logger("vision-demo", "INFO")


# ---------------------------------------------------------------------------
# Dakar traffic simulation parameters
# ---------------------------------------------------------------------------

# Vehicle mix typical for Dakar arterial roads
VEHICLE_MIX = {
    "car": 0.50,
    "motorcycle": 0.20,
    "bus": 0.12,
    "truck": 0.08,
    "person": 0.10,
}

# Hourly traffic multiplier (0=midnight, 7=7am, 17=5pm)
HOUR_FACTORS = {
    0: 0.05, 1: 0.03, 2: 0.03, 3: 0.03, 4: 0.04,
    5: 0.10, 6: 0.35, 7: 0.80, 8: 0.95, 9: 0.85,
    10: 0.70, 11: 0.75, 12: 0.90, 13: 0.85, 14: 0.70,
    15: 0.75, 16: 0.88, 17: 1.00, 18: 0.95, 19: 0.80,
    20: 0.55, 21: 0.40, 22: 0.25, 23: 0.12,
}

# Base vehicles per publish window on a busy Dakar artery
BASE_VEHICLES_PER_WINDOW = 120

# Demo sites and cameras to seed if the DB is empty
DEMO_SITES = [
    {
        "name": "Rond-Point de la Nation",
        "address": "Boulevard de la République, Dakar",
        "city": "Dakar",
        "latitude": 14.6937,
        "longitude": -17.4441,
        "site_type": "intersection",
        "cameras": [
            {"name": "CAM-NATION-01", "stream_url": "rtsp://demo/nation-01", "location_description": "Entrée Nord"},
            {"name": "CAM-NATION-02", "stream_url": "rtsp://demo/nation-02", "location_description": "Entrée Sud"},
        ],
    },
    {
        "name": "Échangeur de Cambérène",
        "address": "Route de Cambérène, Dakar",
        "city": "Dakar",
        "latitude": 14.7319,
        "longitude": -17.4572,
        "site_type": "highway",
        "cameras": [
            {"name": "CAM-CAMB-01", "stream_url": "rtsp://demo/camb-01", "location_description": "Voie principale"},
        ],
    },
    {
        "name": "Carrefour Petersen",
        "address": "Avenue Blaise Diagne, Dakar",
        "city": "Dakar",
        "latitude": 14.6782,
        "longitude": -17.4364,
        "site_type": "intersection",
        "cameras": [
            {"name": "CAM-PETER-01", "stream_url": "rtsp://demo/peter-01", "location_description": "Centre"},
        ],
    },
]


def get_hour_factor() -> float:
    """Return the traffic multiplier for the current hour."""
    hour = datetime.now(timezone.utc).hour
    factor = HOUR_FACTORS.get(hour, 0.5)
    # Add small random noise ±10%
    factor *= random.uniform(0.90, 1.10)
    return factor


def generate_window_counts(factor: float) -> Dict[str, int]:
    """Generate vehicle counts for one time window given a traffic factor."""
    total = max(1, int(BASE_VEHICLES_PER_WINDOW * factor))
    counts: Dict[str, int] = {}
    remaining = total
    classes = list(VEHICLE_MIX.keys())
    for cls in classes[:-1]:
        n = max(0, int(total * VEHICLE_MIX[cls] * random.uniform(0.8, 1.2)))
        counts[cls] = n
        remaining -= n
    counts[classes[-1]] = max(0, remaining)
    return counts


def counts_to_congestion(counts: Dict[str, int], occupancy: float) -> str:
    """Derive congestion level from vehicle count and occupancy."""
    if occupancy >= 0.85:
        return "blocked"
    if occupancy >= 0.65:
        return "heavy"
    if occupancy >= 0.35:
        return "moderate"
    return "free"


def fetch_camera_ids(backend_url: str, auth_headers: Optional[Dict[str, str]] = None) -> List[str]:
    """Fetch active camera IDs from backend API."""
    try:
        resp = requests.get(
            f"{backend_url}/api/cameras/",
            headers=auth_headers or {},
            timeout=10,
        )
        if resp.status_code == 200:
            cameras = resp.json()
            if isinstance(cameras, list) and cameras:
                ids = [str(c.get("id")) for c in cameras if c.get("is_active")]
                if ids:
                    logger.info(f"Fetched {len(ids)} active camera IDs from backend")
                    return ids
    except Exception as exc:
        logger.warning(f"Could not fetch cameras from backend: {exc}")
    return []


def seed_demo_data(backend_url: str, auth_headers: Optional[Dict[str, str]] = None) -> List[str]:
    """
    Create demo sites + cameras in the backend if the DB is empty.
    Returns list of created camera ID strings.
    """
    logger.info("No cameras found — seeding demo data (Dakar intersections)...")
    camera_ids: List[str] = []

    for site_def in DEMO_SITES:
        # Create the site
        site_payload = {k: v for k, v in site_def.items() if k != "cameras"}
        try:
            resp = requests.post(
                f"{backend_url}/api/sites/",
                json=site_payload,
                headers={"Content-Type": "application/json", **(auth_headers or {})},
                timeout=10,
            )
            if resp.status_code not in (200, 201):
                logger.warning(f"Could not create site '{site_def['name']}': {resp.status_code} {resp.text[:200]}")
                continue
            site_id = resp.json().get("id")
            logger.info(f"Created site: {site_def['name']} (id={site_id})")
        except Exception as exc:
            logger.warning(f"Error creating site '{site_def['name']}': {exc}")
            continue

        # Create cameras for this site
        for cam_def in site_def["cameras"]:
            cam_payload = {
                "site_id": site_id,
                "name": cam_def["name"],
                "stream_url": cam_def["stream_url"],
                "location_description": cam_def.get("location_description", ""),
            }
            try:
                resp = requests.post(
                    f"{backend_url}/api/cameras/",
                    json=cam_payload,
                    headers={"Content-Type": "application/json", **(auth_headers or {})},
                    timeout=10,
                )
                if resp.status_code in (200, 201):
                    cam_id = str(resp.json().get("id"))
                    camera_ids.append(cam_id)
                    logger.info(f"  Created camera: {cam_def['name']} (id={cam_id})")
                else:
                    logger.warning(f"  Could not create camera '{cam_def['name']}': {resp.status_code} {resp.text[:200]}")
            except Exception as exc:
                logger.warning(f"  Error creating camera '{cam_def['name']}': {exc}")

    logger.info(f"Demo seed complete: {len(camera_ids)} cameras created")
    return camera_ids


def publish_batch(
    backend_url: str,
    api_key: str,
    events: list,
    max_retries: int = 3,
) -> bool:
    """POST a batch of events to /api/ingest/events."""
    payload = {"events": events}
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    }
    endpoint = f"{backend_url}/api/ingest/events"
    for attempt in range(max_retries):
        try:
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            if resp.status_code in (200, 201):
                logger.info(
                    f"Published {len(events)} events → {resp.json().get('status', 'ok')}"
                )
                return True
            else:
                logger.warning(f"Backend returned {resp.status_code}: {resp.text[:200]}")
                if resp.status_code < 500:
                    return False   # client error → don't retry
        except Exception as exc:
            logger.warning(f"Publish attempt {attempt + 1} failed: {exc}")
        time.sleep(2 ** attempt)
    return False


class DemoPipeline:
    """
    Simulates a multi-camera traffic monitoring scenario for demo/CI.

    Each tick (VISION_PUBLISH_INTERVAL seconds) it generates synthetic
    counts for every active camera and posts them to the backend ingest API.
    """

    def __init__(self):
        import os
        self.backend_url = os.environ.get("VISION_BACKEND_URL", "http://localhost:8000").rstrip("/")
        self.api_key = os.environ.get("VISION_API_KEY", "vision-engine-secret-key")
        self.publish_interval = int(os.environ.get("VISION_PUBLISH_INTERVAL", "30"))
        self.demo_email = os.environ.get("VISION_DEMO_EMAIL", "admin@sentrafic.sn")
        self.demo_password = os.environ.get("VISION_DEMO_PASSWORD", "admin123")
        self.running = True
        signal.signal(signal.SIGINT, self._stop)
        signal.signal(signal.SIGTERM, self._stop)

    def _get_auth_headers(self) -> Dict[str, str]:
        """Try to authenticate against backend and return Bearer headers."""
        try:
            resp = requests.post(
                f"{self.backend_url}/api/auth/login",
                json={"email": self.demo_email, "password": self.demo_password},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if resp.status_code == 200:
                token = resp.json().get("access_token")
                if token:
                    logger.info("Authenticated for demo camera discovery")
                    return {"Authorization": f"Bearer {token}"}
            logger.warning(
                "Could not authenticate for camera discovery: %s %s",
                resp.status_code,
                resp.text[:200],
            )
        except Exception as exc:
            logger.warning(f"Authentication error for camera discovery: {exc}")
        return {}

    def _stop(self, sig, frame):
        logger.info("Demo pipeline stopping...")
        self.running = False
        sys.exit(0)

    def _wait_for_backend(self, timeout: int = 120):
        """Block until the backend health endpoint responds."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                resp = requests.get(f"{self.backend_url}/health", timeout=5)
                if resp.status_code == 200:
                    logger.info("Backend is healthy, starting demo loop")
                    return
            except Exception:
                pass
            logger.info("Waiting for backend to become healthy...")
            time.sleep(5)
        logger.error("Backend not reachable after %ds — aborting", timeout)
        sys.exit(1)

    def _resolve_cameras(self) -> List[str]:
        """
        Return list of camera UUID strings to simulate.
        If no cameras exist yet, seed demo data automatically.
        """
        auth_headers = self._get_auth_headers()
        ids = fetch_camera_ids(self.backend_url, auth_headers=auth_headers)
        if ids:
            return ids

        # DB is empty on first run — create demo sites + cameras
        seeded = seed_demo_data(self.backend_url, auth_headers=auth_headers)
        if seeded:
            return seeded

        logger.error("Could not resolve any camera IDs — will retry on next tick")
        return []

    def run(self):
        logger.info("=== SEN TRAFIC AI — Demo Mode ===")
        logger.info(f"Backend: {self.backend_url}")
        logger.info(f"Publish interval: {self.publish_interval}s")

        self._wait_for_backend()

        # Allow backend seed / Alembic migrations to settle
        time.sleep(3)

        camera_ids = self._resolve_cameras()
        if not camera_ids:
            logger.error("No cameras to simulate — exiting")
            sys.exit(1)

        logger.info(f"Simulating {len(camera_ids)} cameras")

        tick = 0
        while self.running:
            tick += 1
            factor = get_hour_factor()

            events = []
            for cam_id in camera_ids:
                # Each camera gets slightly different traffic
                cam_factor = factor * random.uniform(0.7, 1.3)
                counts = generate_window_counts(cam_factor)
                total = sum(counts.values())

                # Occupancy correlates with vehicle density
                occupancy = min(0.99, cam_factor * 0.65 + random.gauss(0, 0.05))
                occupancy = max(0.0, occupancy)

                congestion = counts_to_congestion(counts, occupancy)

                events.append({
                    "camera_id": cam_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "period_seconds": self.publish_interval,
                    "counts": counts,
                    "avg_occupancy": round(occupancy, 3),
                    "congestion_level": congestion,
                })

            publish_batch(self.backend_url, self.api_key, events)

            # Refresh camera list every 10 ticks in case new cameras were added
            if tick % 10 == 0:
                auth_headers = self._get_auth_headers()
                refreshed = fetch_camera_ids(self.backend_url, auth_headers=auth_headers)
                if refreshed and refreshed != camera_ids:
                    camera_ids = refreshed
                    logger.info(f"Camera list updated: {len(camera_ids)} cameras")

            logger.debug(
                f"Tick {tick} — factor={factor:.2f}, cameras={len(camera_ids)}, "
                f"sleeping {self.publish_interval}s"
            )
            time.sleep(self.publish_interval)


def main():
    pipeline = DemoPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()
