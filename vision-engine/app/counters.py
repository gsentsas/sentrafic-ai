"""
Line counting and stall detection for traffic analysis.
"""

from typing import Dict, Set, Tuple, Optional
from datetime import datetime, timedelta
import cv2
import numpy as np

from app.utils import line_crossed, get_crossing_direction, euclidean_distance
from app.models import TrackState


class LineCounter:
    """
    Counts objects crossing a horizontal line.
    """

    def __init__(self, line_y_ratio: float, frame_height: int):
        """
        Initialize line counter.
        Args:
            line_y_ratio: Y position as ratio of frame height (0-1)
            frame_height: Frame height in pixels
        """
        self.line_y_ratio = line_y_ratio
        self.frame_height = frame_height
        self.line_y = int(line_y_ratio * frame_height)

        # Track crossing history to avoid double-counting
        self.crossed_tracks: Set[int] = set()
        self.counts: Dict[str, int] = {}
        self.directional_counts: Dict[str, Dict[str, int]] = {
            "up": {},
            "down": {},
        }

    def update(
        self,
        prev_pos: Optional[Tuple[float, float]],
        curr_pos: Tuple[float, float],
        track_id: int,
        class_name: str,
    ) -> bool:
        """
        Check if object crossed the line and update counts.
        Args:
            prev_pos: Previous position or None for first detection
            curr_pos: Current position
            track_id: Object track ID
            class_name: Object class name
        Returns:
            True if line was crossed
        """
        if prev_pos is None:
            return False

        # Check if line was crossed
        if not line_crossed(prev_pos, curr_pos, self.line_y):
            return False

        # Avoid double-counting (crossing twice for same object in same frame)
        if track_id in self.crossed_tracks:
            return False

        # Mark as crossed in this update
        self.crossed_tracks.add(track_id)

        # Increment counts
        self.counts[class_name] = self.counts.get(class_name, 0) + 1

        # Track direction
        direction = get_crossing_direction(prev_pos, curr_pos, self.line_y)
        if direction:
            if class_name not in self.directional_counts[direction]:
                self.directional_counts[direction][class_name] = 0
            self.directional_counts[direction][class_name] += 1

        return True

    def reset_frame(self):
        """Reset per-frame tracking (crossed_tracks) for next frame."""
        self.crossed_tracks.clear()

    def get_counts(self) -> Dict[str, int]:
        """Get cumulative crossing counts by class."""
        return self.counts.copy()

    def get_directional_counts(self) -> Dict[str, Dict[str, int]]:
        """Get crossing counts by direction and class."""
        return {
            "up": self.directional_counts["up"].copy(),
            "down": self.directional_counts["down"].copy(),
        }

    def get_total(self) -> int:
        """Get total crossing count."""
        return sum(self.counts.values())

    def reset(self):
        """Reset all counters."""
        self.counts.clear()
        self.directional_counts = {"up": {}, "down": {}}
        self.crossed_tracks.clear()

    def draw(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw counting line and counts on frame.
        Args:
            frame: Input frame
        Returns:
            Frame with line overlay
        """
        frame = frame.copy()
        frame_width = frame.shape[1]

        # Draw line
        cv2.line(frame, (0, self.line_y), (frame_width, self.line_y), (0, 0, 255), 2)

        # Draw counts
        text = f"Total: {self.get_total()}"
        cv2.putText(
            frame,
            text,
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            2,
        )

        # Draw per-class counts
        counts = self.get_counts()
        y_offset = 90
        for class_name, count in sorted(counts.items()):
            text = f"{class_name}: {count}"
            cv2.putText(
                frame,
                text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )
            y_offset += 25

        return frame


class StallDetector:
    """
    Detects vehicles that have stalled (not moving for extended time).
    """

    def __init__(self, stall_threshold_seconds: float = 30.0):
        """
        Initialize stall detector.
        Args:
            stall_threshold_seconds: Time threshold for considering object stalled
        """
        self.stall_threshold = timedelta(seconds=stall_threshold_seconds)
        self.stalled_tracks: Dict[int, bool] = {}
        self.position_history: Dict[int, list] = {}
        self.history_window_frames = 30  # Frames to track for movement

    def update(self, track_states: Dict[int, TrackState]) -> Dict[int, bool]:
        """
        Update stall status for all tracks.
        Args:
            track_states: Dictionary of track_id -> TrackState
        Returns:
            Dictionary mapping track_id to stalled status
        """
        stalled = {}

        for track_id, track in track_states.items():
            current_pos = track.get_current_position()
            if current_pos is None:
                stalled[track_id] = False
                continue

            # Initialize position history for track
            if track_id not in self.position_history:
                self.position_history[track_id] = []

            # Add current position to history
            self.position_history[track_id].append(
                (datetime.utcnow(), current_pos)
            )

            # Keep only recent history
            cutoff_time = datetime.utcnow() - timedelta(seconds=60)
            self.position_history[track_id] = [
                (t, p)
                for t, p in self.position_history[track_id]
                if t > cutoff_time
            ]

            # Calculate displacement over threshold period
            displacement = self._calculate_displacement(track_id)
            is_stalled = displacement < 10.0  # Less than 10 pixels movement

            # Update track state
            track.is_stalled = is_stalled
            stalled[track_id] = is_stalled

        # Cleanup removed tracks
        for track_id in list(self.position_history.keys()):
            if track_id not in track_states:
                del self.position_history[track_id]

        self.stalled_tracks = stalled
        return stalled

    def _calculate_displacement(self, track_id: int) -> float:
        """
        Calculate displacement over threshold period.
        Args:
            track_id: Track identifier
        Returns:
            Displacement in pixels
        """
        if track_id not in self.position_history:
            return 0.0

        history = self.position_history[track_id]
        if len(history) < 2:
            return 0.0

        # Get oldest position within threshold period
        cutoff_time = datetime.utcnow() - self.stall_threshold
        old_positions = [
            (t, p) for t, p in history if t <= cutoff_time
        ]

        if not old_positions:
            # Not enough history, can't determine
            return float("inf")

        old_pos = old_positions[0][1]
        new_pos = history[-1][1]

        return euclidean_distance(old_pos, new_pos)

    def get_stalled_tracks(self) -> Dict[int, bool]:
        """Get all stalled tracks."""
        return self.stalled_tracks.copy()

    def reset(self):
        """Reset all tracking state."""
        self.stalled_tracks.clear()
        self.position_history.clear()

    def draw(self, frame: np.ndarray, track_states: Dict[int, TrackState]) -> np.ndarray:
        """
        Draw stalled vehicle indicators on frame.
        Args:
            frame: Input frame
            track_states: Current track states
        Returns:
            Frame with stall indicators
        """
        frame = frame.copy()

        stalled_count = sum(1 for v in self.stalled_tracks.values() if v)
        text = f"Stalled: {stalled_count}"
        cv2.putText(
            frame,
            text,
            (10, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )

        return frame
