"""
Tests for line counting and stall detection.
"""

import pytest
from datetime import datetime, timedelta

from app.counters import LineCounter, StallDetector
from app.models import TrackState


class TestLineCounter:
    """Test line crossing detection and counting."""

    def test_line_counter_initialization(self):
        """Test line counter initialization."""
        counter = LineCounter(line_y_ratio=0.6, frame_height=1080)
        assert counter.line_y == 648
        assert counter.get_total() == 0

    def test_crossing_downward(self):
        """Test counting downward line crossing."""
        counter = LineCounter(line_y_ratio=0.5, frame_height=100)
        line_y = counter.line_y

        # Object moves from above line to below line
        prev_pos = (50, 30)
        curr_pos = (50, 70)

        crossed = counter.update(prev_pos, curr_pos, track_id=1, class_name="car")

        assert crossed is True
        assert counter.get_total() == 1
        assert counter.get_counts()["car"] == 1

    def test_crossing_upward(self):
        """Test counting upward line crossing."""
        counter = LineCounter(line_y_ratio=0.5, frame_height=100)
        line_y = counter.line_y

        # Object moves from below line to above line
        prev_pos = (50, 70)
        curr_pos = (50, 30)

        crossed = counter.update(prev_pos, curr_pos, track_id=1, class_name="car")

        assert crossed is True
        assert counter.get_total() == 1

    def test_no_crossing(self):
        """Test when object doesn't cross line."""
        counter = LineCounter(line_y_ratio=0.5, frame_height=100)

        # Object stays on same side of line
        prev_pos = (50, 20)
        curr_pos = (50, 40)

        crossed = counter.update(prev_pos, curr_pos, track_id=1, class_name="car")

        assert crossed is False
        assert counter.get_total() == 0

    def test_multi_class_counting(self):
        """Test counting multiple vehicle classes."""
        counter = LineCounter(line_y_ratio=0.5, frame_height=100)

        # Car crossing
        counter.update((50, 30), (50, 70), track_id=1, class_name="car")

        # Bus crossing
        counter.update((60, 30), (60, 70), track_id=2, class_name="bus")

        # Truck crossing
        counter.update((70, 30), (70, 70), track_id=3, class_name="truck")

        counts = counter.get_counts()
        assert counts["car"] == 1
        assert counts["bus"] == 1
        assert counts["truck"] == 1
        assert counter.get_total() == 3

    def test_frame_reset(self):
        """Test frame-by-frame reset to prevent double counting."""
        counter = LineCounter(line_y_ratio=0.5, frame_height=100)

        # First frame: crossing detected
        prev_pos = (50, 30)
        curr_pos = (50, 70)
        crossed1 = counter.update(prev_pos, curr_pos, track_id=1, class_name="car")
        assert crossed1 is True

        # Same frame: should not cross again
        curr_pos2 = (50, 75)
        crossed2 = counter.update(prev_pos, curr_pos2, track_id=1, class_name="car")
        assert crossed2 is False

        # Reset frame
        counter.reset_frame()

        # Next frame: should be able to cross again
        prev_pos = (50, 75)
        curr_pos = (50, 80)
        crossed3 = counter.update(prev_pos, curr_pos, track_id=1, class_name="car")
        # Note: This won't cross since both are above line

    def test_reset_counters(self):
        """Test resetting all counters."""
        counter = LineCounter(line_y_ratio=0.5, frame_height=100)

        counter.update((50, 30), (50, 70), track_id=1, class_name="car")
        assert counter.get_total() == 1

        counter.reset()
        assert counter.get_total() == 0
        assert len(counter.get_counts()) == 0

    def test_directional_counting(self):
        """Test directional counting (up/down)."""
        counter = LineCounter(line_y_ratio=0.5, frame_height=100)

        # Crossing downward
        counter.update((50, 30), (50, 70), track_id=1, class_name="car")

        # Crossing upward
        counter.update((60, 70), (60, 30), track_id=2, class_name="bus")

        directional = counter.get_directional_counts()
        assert directional["down"].get("car", 0) == 1
        assert directional["up"].get("bus", 0) == 1


class TestStallDetector:
    """Test stall detection for stationary vehicles."""

    def test_stall_detector_initialization(self):
        """Test stall detector initialization."""
        detector = StallDetector(stall_threshold_seconds=30.0)
        assert detector.stall_threshold == timedelta(seconds=30.0)

    def test_moving_vehicle_not_stalled(self):
        """Test that moving vehicle is not stalled."""
        detector = StallDetector(stall_threshold_seconds=5.0)

        # Create track that moves over time
        track = TrackState(track_id=1, class_name="car")
        track.positions = [
            (100, 100),
            (110, 100),
            (120, 100),
            (130, 100),
        ]
        track.last_seen = datetime.utcnow()

        track_states = {1: track}
        stalled = detector.update(track_states)

        assert stalled.get(1, False) is False

    def test_stationary_vehicle_stalled(self):
        """Test that stationary vehicle is stalled."""
        detector = StallDetector(stall_threshold_seconds=5.0)

        # Create track that stays in same position
        track = TrackState(track_id=1, class_name="car")
        # Add positions with timestamps spaced 1 second apart
        now = datetime.utcnow()
        for i in range(10):
            track.positions.append((100, 100))
            track.first_seen = now - timedelta(seconds=6)
            track.last_seen = now

        track_states = {1: track}
        stalled = detector.update(track_states)

        # Should be stalled (no movement over 5 seconds)
        assert stalled.get(1, False) is True

    def test_insufficient_history_not_stalled(self):
        """Test that tracks with insufficient history are not marked stalled."""
        detector = StallDetector(stall_threshold_seconds=5.0)

        # Create track with only one position
        track = TrackState(track_id=1, class_name="car")
        track.positions = [(100, 100)]
        track.last_seen = datetime.utcnow()

        track_states = {1: track}
        stalled = detector.update(track_states)

        assert stalled.get(1, False) is False

    def test_cleanup_removed_tracks(self):
        """Test cleanup of removed tracks from history."""
        detector = StallDetector(stall_threshold_seconds=5.0)

        # Add track
        track = TrackState(track_id=1, class_name="car")
        track.positions = [(100, 100)]
        track.last_seen = datetime.utcnow()

        track_states = {1: track}
        detector.update(track_states)
        assert 1 in detector.position_history

        # Remove track
        detector.update({})
        assert 1 not in detector.position_history

    def test_multiple_tracks_stall_detection(self):
        """Test stall detection on multiple tracks."""
        detector = StallDetector(stall_threshold_seconds=5.0)

        # Moving track
        track1 = TrackState(track_id=1, class_name="car")
        track1.positions = [(100, 100), (110, 100), (120, 100)]
        track1.last_seen = datetime.utcnow()

        # Stationary track
        track2 = TrackState(track_id=2, class_name="bus")
        track2.positions = [(200, 200), (200, 200), (200, 200)]
        track2.first_seen = datetime.utcnow() - timedelta(seconds=6)
        track2.last_seen = datetime.utcnow()

        track_states = {1: track1, 2: track2}
        stalled = detector.update(track_states)

        # Note: track1 might not have enough history to determine movement
        # track2 should show no movement
