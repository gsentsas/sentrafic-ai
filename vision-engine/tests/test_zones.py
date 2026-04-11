"""
Tests for zone monitoring and polygon geometry.
"""

import pytest
from datetime import datetime

from app.zones import ZoneCounter, MultiZoneCounter
from app.models import TrackState
from app.utils import point_in_polygon


class TestPointInPolygon:
    """Test point-in-polygon detection (ray casting algorithm)."""

    def test_point_inside_square(self):
        """Test point clearly inside square."""
        polygon = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        point = (0.5, 0.5)
        assert point_in_polygon(point, polygon) is True

    def test_point_outside_square(self):
        """Test point clearly outside square."""
        polygon = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        point = (1.5, 0.5)
        assert point_in_polygon(point, polygon) is False

    def test_point_on_vertex(self):
        """Test point on vertex."""
        polygon = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        point = (0.0, 0.0)
        # Ray casting may or may not include boundary points
        result = point_in_polygon(point, polygon)
        assert isinstance(result, bool)

    def test_triangle_point_inside(self):
        """Test point inside triangle."""
        polygon = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        point = (0.5, 0.4)
        assert point_in_polygon(point, polygon) is True

    def test_triangle_point_outside(self):
        """Test point outside triangle."""
        polygon = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        point = (0.5, 1.5)
        assert point_in_polygon(point, polygon) is False

    def test_complex_polygon(self):
        """Test point in complex polygon."""
        # Pentagon-like shape
        polygon = [
            (0.3, 0.1),
            (0.7, 0.1),
            (0.9, 0.5),
            (0.5, 0.9),
            (0.1, 0.5),
        ]

        # Inside points
        assert point_in_polygon((0.5, 0.5), polygon) is True
        assert point_in_polygon((0.5, 0.3), polygon) is True

        # Outside points
        assert point_in_polygon((0.0, 0.0), polygon) is False
        assert point_in_polygon((1.0, 1.0), polygon) is False


class TestZoneCounter:
    """Test zone occupancy monitoring."""

    def test_zone_counter_initialization(self):
        """Test zone counter initialization."""
        polygon = [(0.2, 0.3), (0.8, 0.3), (0.8, 0.9), (0.2, 0.9)]
        counter = ZoneCounter(polygon, frame_width=640, frame_height=480)

        assert counter.get_count() == 0
        assert len(counter.pixel_polygon) == 4

    def test_object_in_zone(self):
        """Test detection of object in zone."""
        polygon = [(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]
        counter = ZoneCounter(polygon, frame_width=640, frame_height=480)

        # Track at center of zone (normalized coordinates)
        track = TrackState(track_id=1, class_name="car")
        track.positions = [(0.5, 0.5)]  # Center of zone

        track_states = {1: track}
        occupancy = counter.update(track_states)

        assert counter.get_count() == 1
        assert occupancy > 0.0

    def test_object_outside_zone(self):
        """Test object outside zone is not counted."""
        polygon = [(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]
        counter = ZoneCounter(polygon, frame_width=640, frame_height=480)

        # Track outside zone
        track = TrackState(track_id=1, class_name="car")
        track.positions = [(0.1, 0.1)]  # Outside zone

        track_states = {1: track}
        occupancy = counter.update(track_states)

        assert counter.get_count() == 0
        assert occupancy == 0.0

    def test_multiple_objects_in_zone(self):
        """Test counting multiple objects in zone."""
        polygon = [(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]
        counter = ZoneCounter(polygon, frame_width=640, frame_height=480)

        # Create multiple tracks in zone
        track1 = TrackState(track_id=1, class_name="car")
        track1.positions = [(0.4, 0.4)]

        track2 = TrackState(track_id=2, class_name="bus")
        track2.positions = [(0.6, 0.6)]

        track3 = TrackState(track_id=3, class_name="motorcycle")
        track3.positions = [(0.3, 0.7)]

        track_states = {1: track1, 2: track2, 3: track3}
        occupancy = counter.update(track_states)

        assert counter.get_count() == 3
        assert occupancy > 0.0

    def test_count_by_class(self):
        """Test counting objects by class."""
        polygon = [(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]
        counter = ZoneCounter(polygon, frame_width=640, frame_height=480)

        # Create tracks of different classes
        track1 = TrackState(track_id=1, class_name="car")
        track1.positions = [(0.4, 0.4)]

        track2 = TrackState(track_id=2, class_name="car")
        track2.positions = [(0.5, 0.5)]

        track3 = TrackState(track_id=3, class_name="bus")
        track3.positions = [(0.6, 0.6)]

        track_states = {1: track1, 2: track2, 3: track3}
        counter.update(track_states)

        counts = counter.get_count_by_class()
        assert counts["car"] == 2
        assert counts["bus"] == 1

    def test_occupancy_calculation(self):
        """Test occupancy ratio calculation."""
        polygon = [(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]
        counter = ZoneCounter(polygon, frame_width=640, frame_height=480)

        # Empty zone
        occupancy1 = counter.update({})
        assert occupancy1 == 0.0

        # One object
        track1 = TrackState(track_id=1, class_name="car")
        track1.positions = [(0.5, 0.5)]
        occupancy2 = counter.update({1: track1})
        assert occupancy2 > 0.0

        # More objects
        track2 = TrackState(track_id=2, class_name="car")
        track2.positions = [(0.4, 0.4)]
        track3 = TrackState(track_id=3, class_name="car")
        track3.positions = [(0.6, 0.6)]
        occupancy3 = counter.update({1: track1, 2: track2, 3: track3})
        assert occupancy3 > occupancy2

    def test_is_in_zone(self):
        """Test checking if specific object is in zone."""
        polygon = [(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]
        counter = ZoneCounter(polygon, frame_width=640, frame_height=480)

        track = TrackState(track_id=1, class_name="car")
        track.positions = [(0.5, 0.5)]
        counter.update({1: track})

        assert counter.is_in_zone(1) is True
        assert counter.is_in_zone(999) is False


class TestMultiZoneCounter:
    """Test multiple zone monitoring."""

    def test_multi_zone_initialization(self):
        """Test multi-zone counter initialization."""
        zones = [
            [(0.0, 0.0), (0.5, 0.0), (0.5, 1.0), (0.0, 1.0)],  # Left zone
            [(0.5, 0.0), (1.0, 0.0), (1.0, 1.0), (0.5, 1.0)],  # Right zone
        ]
        counter = MultiZoneCounter(zones, frame_width=640, frame_height=480)

        assert len(counter.zones) == 2
        assert counter.zone_names == ["Zone 0", "Zone 1"]

    def test_multi_zone_with_names(self):
        """Test multi-zone counter with custom names."""
        zones = [
            [(0.0, 0.0), (0.5, 0.0), (0.5, 1.0), (0.0, 1.0)],
            [(0.5, 0.0), (1.0, 0.0), (1.0, 1.0), (0.5, 1.0)],
        ]
        names = ["Left Lane", "Right Lane"]
        counter = MultiZoneCounter(zones, frame_width=640, frame_height=480, zone_names=names)

        assert counter.zone_names == names

    def test_multi_zone_object_assignment(self):
        """Test objects assigned to correct zones."""
        zones = [
            [(0.0, 0.0), (0.5, 0.0), (0.5, 1.0), (0.0, 1.0)],  # Left
            [(0.5, 0.0), (1.0, 0.0), (1.0, 1.0), (0.5, 1.0)],  # Right
        ]
        names = ["Left", "Right"]
        counter = MultiZoneCounter(zones, frame_width=640, frame_height=480, zone_names=names)

        # Create tracks in each zone
        track_left = TrackState(track_id=1, class_name="car")
        track_left.positions = [(0.25, 0.5)]

        track_right = TrackState(track_id=2, class_name="car")
        track_right.positions = [(0.75, 0.5)]

        track_states = {1: track_left, 2: track_right}
        results = counter.update(track_states)

        assert results["Left"]["count"] == 1
        assert results["Right"]["count"] == 1
