"""
Multi-object tracking using YOLO's built-in ByteTrack.
"""

from typing import List, Dict, Optional
import cv2
import numpy as np
from datetime import datetime

from app.config import Settings
from app.models import Detection, TrackState


class ObjectTracker:
    """
    Wraps YOLO's built-in tracking with ByteTrack.
    """

    def __init__(self, config: Settings, model):
        """
        Initialize tracker.
        Args:
            config: Settings configuration
            model: YOLO model instance
        """
        self.config = config
        self.model = model
        self.track_states: Dict[int, TrackState] = {}
        self.coco_to_target = config.get_coco_to_target_mapping()
        self.target_coco_ids = set(self.coco_to_target.keys())

    def update(
        self, frame: np.ndarray
    ) -> tuple[List[Detection], Dict[int, TrackState]]:
        """
        Run detection and tracking on frame.
        Args:
            frame: Input frame
        Returns:
            Tuple of (list of detections, updated track states)
        """
        # Run YOLO with tracking
        results = self.model.track(
            frame,
            conf=self.config.yolo_confidence,
            iou=self.config.yolo_iou,
            persist=True,
            tracker="bytetrack.yaml",
        )

        detections: List[Detection] = []
        current_track_ids = set()

        if results and results[0].boxes is not None:
            boxes = results[0].boxes

            for i in range(len(boxes)):
                # Get class ID
                class_id = int(boxes.cls[i])

                # Filter to target classes only
                if class_id not in self.target_coco_ids:
                    continue

                # Get track ID
                track_id = None
                if boxes.id is not None:
                    track_id = int(boxes.id[i])

                # Get confidence
                confidence = float(boxes.conf[i])

                # Get bounding box
                box = boxes.xyxy[i]
                x1, y1, x2, y2 = float(box[0]), float(box[1]), float(box[2]), float(box[3])
                bbox = (x1, y1, x2, y2)

                # Map COCO class to target class
                class_name = self.coco_to_target.get(class_id, "unknown")

                # Create detection
                detection = Detection(
                    class_name=class_name,
                    confidence=confidence,
                    bbox=bbox,
                    track_id=track_id,
                )
                detections.append(detection)

                # Update or create track state
                if track_id is not None:
                    current_track_ids.add(track_id)
                    cx, cy = detection.get_center()

                    if track_id not in self.track_states:
                        self.track_states[track_id] = TrackState(
                            track_id=track_id,
                            class_name=class_name,
                        )

                    track = self.track_states[track_id]
                    track.update_position((cx, cy))
                    track.class_name = class_name

        # Remove old tracks that are no longer detected
        self.cleanup_old_tracks(max_age_seconds=30)

        return detections, self.track_states

    def get_track_states(self) -> Dict[int, TrackState]:
        """Get all current track states."""
        return self.track_states.copy()

    def cleanup_old_tracks(self, max_age_seconds: float = 30.0):
        """
        Remove tracks that haven't been updated recently.
        Args:
            max_age_seconds: Maximum age in seconds before removing
        """
        current_time = datetime.utcnow()
        to_remove = []

        for track_id, track in self.track_states.items():
            age = (current_time - track.last_seen).total_seconds()
            if age > max_age_seconds:
                to_remove.append(track_id)

        for track_id in to_remove:
            del self.track_states[track_id]

    def reset(self):
        """Reset all tracking state."""
        self.track_states.clear()


class DetectionBuffer:
    """
    Buffers detections to smooth tracking and reduce noise.
    """

    def __init__(self, buffer_size: int = 3):
        """
        Initialize detection buffer.
        Args:
            buffer_size: Number of frames to buffer
        """
        self.buffer_size = buffer_size
        self.buffer: List[List[Detection]] = []

    def add(self, detections: List[Detection]):
        """Add frame detections to buffer."""
        self.buffer.append(detections)
        if len(self.buffer) > self.buffer_size:
            self.buffer.pop(0)

    def get_smoothed(self) -> List[Detection]:
        """
        Get detections smoothed over buffered frames.
        Uses majority voting for track IDs.
        """
        if not self.buffer:
            return []

        # For now, return latest detections
        # Could implement smoothing here
        return self.buffer[-1]

    def clear(self):
        """Clear buffer."""
        self.buffer.clear()
