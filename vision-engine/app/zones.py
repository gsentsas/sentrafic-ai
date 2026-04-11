"""
Zone monitoring for traffic analysis.
Tracks vehicle occupancy within defined polygonal zones.
"""

from typing import List, Dict, Tuple, Optional
import cv2
import numpy as np

from app.models import Detection, TrackState, ZonePolygon
from app.utils import point_in_polygon


class ZoneCounter:
    """
    Monitors object occupancy within a polygonal zone.
    """

    def __init__(
        self,
        polygon_points: List[Tuple[float, float]],
        frame_width: int,
        frame_height: int,
    ):
        """
        Initialize zone counter.
        Args:
            polygon_points: List of (x, y) normalized coordinates (0-1)
            frame_width: Frame width in pixels
            frame_height: Frame height in pixels
        """
        self.polygon_points = polygon_points
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.objects_in_zone: Dict[int, str] = {}  # track_id -> class_name

        # Convert normalized points to pixel coordinates
        self.pixel_polygon = [
            (int(x * frame_width), int(y * frame_height))
            for x, y in polygon_points
        ]

        # Create zone polygon model
        self.zone_polygon = ZonePolygon(points=polygon_points)

    def update(self, track_states: Dict[int, TrackState]) -> float:
        """
        Update zone occupancy based on current tracks.
        Args:
            track_states: Dictionary of track_id -> TrackState
        Returns:
            Zone occupancy as float (0-1)
        """
        self.objects_in_zone.clear()

        for track_id, track in track_states.items():
            position = track.get_current_position()
            if position is None:
                continue

            # Check if position is inside zone
            if point_in_polygon(position, self.polygon_points):
                self.objects_in_zone[track_id] = track.class_name

        # Calculate occupancy (normalized by zone area)
        zone_area = self._calculate_polygon_area()
        if zone_area == 0:
            return 0.0

        # Occupancy is count normalized by a reference area
        # Use simple ratio: current_objects / max_reasonable_objects
        max_objects = max(10, int(zone_area / 10000))  # Rough estimate
        occupancy = min(1.0, len(self.objects_in_zone) / max_objects)
        return occupancy

    def get_count(self) -> int:
        """Get number of objects currently in zone."""
        return len(self.objects_in_zone)

    def get_count_by_class(self) -> Dict[str, int]:
        """Get count of objects in zone by class."""
        counts: Dict[str, int] = {}
        for class_name in self.objects_in_zone.values():
            counts[class_name] = counts.get(class_name, 0) + 1
        return counts

    def is_in_zone(self, track_id: int) -> bool:
        """Check if specific object is in zone."""
        return track_id in self.objects_in_zone

    def draw(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw zone polygon on frame.
        Args:
            frame: Input frame
        Returns:
            Frame with zone overlay
        """
        frame = frame.copy()

        # Draw zone polygon
        points_array = np.array(self.pixel_polygon, dtype=np.int32)
        cv2.polylines(frame, [points_array], True, (0, 255, 0), 2)
        cv2.fillPoly(frame, [points_array], (0, 255, 0), alpha=0.1)

        # Draw object count in zone
        count = self.get_count()
        text = f"Zone: {count} objects"
        cv2.putText(
            frame,
            text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            2,
        )

        return frame

    def _calculate_polygon_area(self) -> float:
        """
        Calculate area of polygon using shoelace formula.
        Returns:
            Area in pixels squared
        """
        points = self.pixel_polygon
        n = len(points)
        if n < 3:
            return 0.0

        area = 0.0
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            area += x1 * y2 - x2 * y1

        return abs(area) / 2.0


class MultiZoneCounter:
    """
    Manages multiple overlapping zones.
    """

    def __init__(
        self,
        zone_definitions: List[List[Tuple[float, float]]],
        frame_width: int,
        frame_height: int,
        zone_names: Optional[List[str]] = None,
    ):
        """
        Initialize multi-zone counter.
        Args:
            zone_definitions: List of zone polygon point lists
            frame_width: Frame width in pixels
            frame_height: Frame height in pixels
            zone_names: Optional names for zones
        """
        self.zones = [
            ZoneCounter(points, frame_width, frame_height)
            for points in zone_definitions
        ]
        self.zone_names = zone_names or [f"Zone {i}" for i in range(len(self.zones))]

    def update(self, track_states: Dict[int, TrackState]) -> Dict[str, Dict]:
        """
        Update all zones.
        Args:
            track_states: Dictionary of track_id -> TrackState
        Returns:
            Dictionary mapping zone names to zone stats
        """
        results = {}
        for zone, name in zip(self.zones, self.zone_names):
            occupancy = zone.update(track_states)
            results[name] = {
                "occupancy": occupancy,
                "count": zone.get_count(),
                "by_class": zone.get_count_by_class(),
            }
        return results

    def draw_all(self, frame: np.ndarray) -> np.ndarray:
        """Draw all zones on frame."""
        for zone in self.zones:
            frame = zone.draw(frame)
        return frame
