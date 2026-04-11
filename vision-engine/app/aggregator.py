"""
Traffic metrics aggregation over time windows.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

from app.models import FrameResult, AggregateResult
from app.utils import calculate_congestion

logger = logging.getLogger(__name__)


class TrafficAggregator:
    """
    Aggregates traffic metrics over configurable time windows.
    """

    def __init__(self, window_seconds: int = 300, camera_id: str = "1"):
        """
        Initialize aggregator.
        Args:
            window_seconds: Aggregation window in seconds
            camera_id: Camera identifier
        """
        self.window_seconds = window_seconds
        self.camera_id = camera_id

        # Current window state
        self.window_start: Optional[datetime] = None
        self.counts: Dict[str, int] = {}
        self.occupancy_samples: List[float] = []
        self.frame_count = 0

    def update(self, frame_result: FrameResult) -> Optional[AggregateResult]:
        """
        Update aggregator with frame result.
        Yields AggregateResult when window expires.
        Args:
            frame_result: FrameResult from frame processing
        Returns:
            AggregateResult if window expired, else None
        """
        # Initialize window if needed
        if self.window_start is None:
            self.window_start = frame_result.timestamp

        # Accumulate counts
        for detection in frame_result.detections:
            self.counts[detection.class_name] = (
                self.counts.get(detection.class_name, 0) + 1
            )

        # Track occupancy
        self.occupancy_samples.append(frame_result.zone_occupancy)
        self.frame_count += 1

        # Check if window has expired
        elapsed = (
            frame_result.timestamp - self.window_start
        ).total_seconds()

        if elapsed >= self.window_seconds:
            return self._finalize_window(frame_result.timestamp)

        return None

    def _finalize_window(
        self, end_timestamp: datetime
    ) -> Optional[AggregateResult]:
        """
        Finalize current window and create AggregateResult.
        Args:
            end_timestamp: Timestamp for window end
        Returns:
            AggregateResult with aggregated metrics
        """
        if self.window_start is None:
            return None

        # Calculate average occupancy
        avg_occupancy = (
            sum(self.occupancy_samples) / len(self.occupancy_samples)
            if self.occupancy_samples
            else 0.0
        )

        # Calculate congestion level
        total_vehicles = sum(self.counts.values())
        congestion_level = calculate_congestion(avg_occupancy, total_vehicles)

        # Create aggregate result
        result = AggregateResult(
            camera_id=self.camera_id,
            timestamp=self.window_start,
            period_seconds=self.window_seconds,
            counts=self.counts.copy(),
            avg_occupancy=avg_occupancy,
            congestion_level=congestion_level,
        )

        logger.info(
            f"Window finalized: {total_vehicles} vehicles, "
            f"occupancy={avg_occupancy:.2%}, level={congestion_level}"
        )

        # Reset for next window
        self.reset()
        self.window_start = end_timestamp

        return result

    def reset(self):
        """Reset aggregator state for next window."""
        self.window_start = None
        self.counts.clear()
        self.occupancy_samples.clear()
        self.frame_count = 0

    def get_current_state(self) -> Dict:
        """Get current aggregation state."""
        if self.window_start is None:
            return {}

        return {
            "window_start": self.window_start.isoformat(),
            "counts": self.counts.copy(),
            "occupancy_samples": len(self.occupancy_samples),
            "frame_count": self.frame_count,
        }


class MultiWindowAggregator:
    """
    Manages multiple aggregation windows (e.g., 1-minute, 5-minute, 15-minute).
    """

    def __init__(
        self,
        window_sizes: List[int] = None,
        camera_id: str = "1",
    ):
        """
        Initialize multi-window aggregator.
        Args:
            window_sizes: List of window sizes in seconds
            camera_id: Camera identifier
        """
        self.window_sizes = window_sizes or [60, 300, 900]  # 1m, 5m, 15m
        self.camera_id = camera_id
        self.aggregators = [
            TrafficAggregator(window_seconds=size, camera_id=camera_id)
            for size in self.window_sizes
        ]
        self.results: Dict[int, AggregateResult] = {}

    def update(self, frame_result: FrameResult) -> Dict[int, AggregateResult]:
        """
        Update all windows.
        Args:
            frame_result: FrameResult from frame processing
        Returns:
            Dictionary mapping window size to AggregateResult if expired
        """
        self.results.clear()

        for aggregator in self.aggregators:
            result = aggregator.update(frame_result)
            if result is not None:
                self.results[aggregator.window_seconds] = result

        return self.results

    def get_results(self) -> Dict[int, AggregateResult]:
        """Get all finalized results."""
        return self.results.copy()
