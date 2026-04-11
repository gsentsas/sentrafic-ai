"""
Main pipeline orchestrator for the vision engine.
Coordinates detection, tracking, counting, and publishing.
"""

import signal
import sys
import logging
import time
from datetime import datetime
import cv2
import numpy as np

from app.config import load_config
from app.detector import ObjectDetector
from app.tracker import ObjectTracker
from app.stream import VideoStream
from app.counters import LineCounter, StallDetector
from app.zones import ZoneCounter
from app.aggregator import TrafficAggregator
from app.publisher import ResultPublisher
from app.models import FrameResult, TrackState
from app.utils import setup_logger


class Pipeline:
    """
    Main processing pipeline for traffic analysis.
    """

    def __init__(self):
        """Initialize pipeline components."""
        self.config = load_config()
        self.logger = setup_logger("vision-engine", self.config.log_level)
        self.logger.info("Initializing vision engine pipeline...")

        # Load YOLO model
        self.logger.info(f"Loading YOLO model: {self.config.yolo_model}")
        from ultralytics import YOLO
        self.yolo_model = YOLO(self.config.yolo_model)

        # Initialize components
        self.detector = ObjectDetector(self.config)
        self.tracker = ObjectTracker(self.config, self.yolo_model)
        self.stream = VideoStream(self.config.vision_source)

        # Initialize counters and monitors
        self.line_counter = LineCounter(
            self.config.line_y_ratio, 0
        )  # Height set after stream opens
        self.stall_detector = StallDetector(stall_threshold_seconds=30.0)
        self.zone_counter = None  # Initialized after stream opens

        # Initialize aggregation and publishing
        self.aggregator = TrafficAggregator(
            window_seconds=self.config.publish_interval,
            camera_id=self.config.vision_camera_id,
        )
        self.publisher = ResultPublisher(
            backend_url=self.config.backend_url,
            api_key=self.config.backend_api_key,
            camera_id=self.config.vision_camera_id,
        )

        # State
        self.running = True
        self.frame_count = 0
        self.total_detections = 0
        self.start_time = datetime.utcnow()

        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.logger.info("Pipeline initialization complete")

    def _signal_handler(self, sig, frame):
        """Handle shutdown signals."""
        self.logger.info("Shutdown signal received, cleaning up...")
        self.running = False
        self.cleanup()
        sys.exit(0)

    def run(self):
        """Main pipeline loop."""
        try:
            self._initialize_stream()
            self._main_loop()
        except Exception as e:
            self.logger.error(f"Pipeline error: {e}", exc_info=True)
        finally:
            self.cleanup()

    def _initialize_stream(self):
        """Open and validate video stream."""
        self.logger.info(f"Opening video stream: {self.config.vision_source}")

        if not self.stream.open():
            raise RuntimeError("Failed to open video stream")

        # Get stream properties
        frame_width, frame_height = self.stream.get_frame_size()
        fps = self.stream.get_fps()

        if frame_width == 0 or frame_height == 0:
            raise RuntimeError("Invalid frame dimensions")

        self.logger.info(
            f"Stream opened: {frame_width}x{frame_height} @ {fps:.2f} fps"
        )

        # Initialize components that need frame dimensions
        self.line_counter = LineCounter(
            self.config.line_y_ratio, frame_height
        )

        # Initialize zone counter
        zone_points = self.config.parse_zone_points()
        self.zone_counter = ZoneCounter(zone_points, frame_width, frame_height)

        self.logger.info("Stream initialization complete")

    def _main_loop(self):
        """Main processing loop."""
        self.logger.info("Starting main processing loop...")

        frame_width, frame_height = self.stream.get_frame_size()
        prev_frame_time = time.time()
        frame_times = []

        while self.running:
            # Read frame
            ret, frame = self.stream.read()

            if not ret:
                if self.stream.is_rtsp:
                    self.logger.warning("Stream ended, waiting for reconnection...")
                    time.sleep(2)
                    continue
                else:
                    self.logger.info("Video file ended")
                    break

            self.frame_count += 1

            # Detect objects
            detections = self.detector.detect(frame)
            self.total_detections += len(detections)

            # Track objects
            tracked_detections, track_states = self.tracker.update(frame)

            # Update counters and monitors
            self.line_counter.reset_frame()

            for detection in tracked_detections:
                track_id = detection.track_id
                if track_id is not None and track_id in track_states:
                    track = track_states[track_id]
                    if len(track.positions) > 1:
                        prev_pos = track.positions[-2]
                        curr_pos = track.positions[-1]
                        self.line_counter.update(
                            prev_pos, curr_pos, track_id, detection.class_name
                        )

            # Update zone counter
            zone_occupancy = self.zone_counter.update(track_states)

            # Update stall detector
            self.stall_detector.update(track_states)

            # Create frame result
            frame_result = FrameResult(
                frame_number=self.frame_count,
                timestamp=datetime.utcnow(),
                detections=detections,
                active_tracks=len(track_states),
                zone_occupancy=zone_occupancy,
            )

            # Feed to aggregator
            agg_result = self.aggregator.update(frame_result)

            # Publish if window completed
            if agg_result is not None:
                self.logger.info(
                    f"Publishing aggregated result: {agg_result.counts}"
                )
                self.publisher.publish(agg_result)

            # Optional: Display output
            if self.config.display_output:
                frame = self._draw_overlays(frame, detections, track_states)
                cv2.imshow("Vision Engine", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self.running = False

            # Performance tracking
            current_time = time.time()
            frame_time = current_time - prev_frame_time
            frame_times.append(frame_time)
            if len(frame_times) > 100:
                frame_times.pop(0)

            if self.frame_count % 100 == 0:
                avg_fps = 1.0 / (sum(frame_times) / len(frame_times))
                self.logger.info(
                    f"Frame {self.frame_count}: "
                    f"{len(tracked_detections)} detections, "
                    f"{len(track_states)} active tracks, "
                    f"{avg_fps:.1f} fps"
                )

            prev_frame_time = current_time

        # Flush any queued results
        self.logger.info("Flushing queued results...")
        self.publisher.flush_queue()

    def _draw_overlays(self, frame, detections, track_states):
        """Draw visualization overlays on frame."""
        frame = frame.copy()

        # Draw detections with bounding boxes
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # Draw bounding box
            color = (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Draw label
            label = f"{detection.class_name} {detection.confidence:.2f}"
            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )

        # Draw tracking IDs
        for track_id, track in track_states.items():
            pos = track.get_current_position()
            if pos is not None:
                x, y = int(pos[0]), int(pos[1])
                cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)
                cv2.putText(
                    frame,
                    f"ID:{track_id}",
                    (x + 10, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 0, 0),
                    2,
                )

        # Draw counters
        frame = self.line_counter.draw(frame)
        frame = self.zone_counter.draw(frame)
        frame = self.stall_detector.draw(frame, track_states)

        # Draw stats
        stats_text = f"Frame: {self.frame_count} | Tracks: {len(track_states)}"
        cv2.putText(
            frame,
            stats_text,
            (10, frame.shape[0] - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        return frame

    def cleanup(self):
        """Clean up resources."""
        self.logger.info("Cleaning up resources...")

        if self.stream:
            self.stream.close()

        if self.config.display_output:
            cv2.destroyAllWindows()

        # Print final stats
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        self.logger.info(f"Pipeline stopped after {elapsed:.1f} seconds")
        self.logger.info(f"Total frames: {self.frame_count}")
        self.logger.info(f"Total detections: {self.total_detections}")
        self.logger.info(f"Publisher stats: {self.publisher.get_stats()}")

        self.logger.info("Cleanup complete")


def main():
    """Entry point."""
    pipeline = Pipeline()
    pipeline.run()


if __name__ == "__main__":
    main()
