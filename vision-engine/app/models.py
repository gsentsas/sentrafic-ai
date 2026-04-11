"""
Data models for the vision engine.
Represents detections, tracks, and aggregated results.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime


@dataclass
class Detection:
    """Single object detection result."""

    class_name: str
    confidence: float
    bbox: Tuple[float, float, float, float]  # (x1, y1, x2, y2)
    track_id: Optional[int] = None

    def get_center(self) -> Tuple[float, float]:
        """Get bounding box center point."""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def get_area(self) -> float:
        """Get bounding box area in pixels."""
        x1, y1, x2, y2 = self.bbox
        return max(0, (x2 - x1) * (y2 - y1))


@dataclass
class TrackState:
    """State of a tracked object over time."""

    track_id: int
    class_name: str
    positions: List[Tuple[float, float]] = field(default_factory=list)
    crossed_line: bool = False
    in_zone: bool = False
    last_seen: datetime = field(default_factory=datetime.utcnow)
    is_stalled: bool = False
    first_seen: datetime = field(default_factory=datetime.utcnow)

    def get_current_position(self) -> Optional[Tuple[float, float]]:
        """Get most recent position."""
        return self.positions[-1] if self.positions else None

    def get_displacement(self) -> float:
        """Get total displacement from first to last position."""
        if len(self.positions) < 2:
            return 0.0
        start = self.positions[0]
        end = self.positions[-1]
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        return (dx * dx + dy * dy) ** 0.5

    def update_position(self, position: Tuple[float, float]) -> None:
        """Add a new position to track history."""
        self.positions.append(position)
        self.last_seen = datetime.utcnow()

    def age_seconds(self) -> float:
        """Get age of track in seconds."""
        return (datetime.utcnow() - self.first_seen).total_seconds()

    def time_since_seen_seconds(self) -> float:
        """Get seconds since last update."""
        return (datetime.utcnow() - self.last_seen).total_seconds()


@dataclass
class FrameResult:
    """Analysis result for a single frame."""

    frame_number: int
    timestamp: datetime
    detections: List[Detection] = field(default_factory=list)
    active_tracks: int = 0
    zone_occupancy: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "frame_number": self.frame_number,
            "timestamp": self.timestamp.isoformat(),
            "detection_count": len(self.detections),
            "active_tracks": self.active_tracks,
            "zone_occupancy": self.zone_occupancy,
        }


@dataclass
class AggregateResult:
    """Aggregated traffic metrics over a time window."""

    camera_id: str
    timestamp: datetime
    period_seconds: int
    counts: Dict[str, int] = field(default_factory=dict)
    avg_occupancy: float = 0.0
    congestion_level: str = "free"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "camera_id": self.camera_id,
            "timestamp": self.timestamp.isoformat(),
            "period_seconds": self.period_seconds,
            "counts": self.counts,
            "avg_occupancy": self.avg_occupancy,
            "congestion_level": self.congestion_level,
        }

    def to_json_payload(self) -> Dict:
        """Generate payload for backend API."""
        return {
            "camera_id": self.camera_id,
            "timestamp": self.timestamp.isoformat(),
            "period_seconds": self.period_seconds,
            "counts": self.counts,
            "avg_occupancy": round(self.avg_occupancy, 3),
            "congestion_level": self.congestion_level,
        }


@dataclass
class CounterLine:
    """Configuration for a counting line."""

    y_position: int
    direction: str = "both"  # "up", "down", or "both"

    def __post_init__(self):
        if self.direction not in ("up", "down", "both"):
            raise ValueError(f"Invalid direction: {self.direction}")


@dataclass
class ZonePolygon:
    """Configuration for a detection zone."""

    points: List[Tuple[float, float]]

    def __post_init__(self):
        if len(self.points) < 3:
            raise ValueError("Zone must have at least 3 points")
