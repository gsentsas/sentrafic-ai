"""
YOLO-based object detection for traffic analysis.
"""

from typing import List
import cv2
import numpy as np
from ultralytics import YOLO

from app.config import Settings
from app.models import Detection


class ObjectDetector:
    """
    YOLO-based detector for target classes.
    """

    def __init__(self, config: Settings):
        """
        Initialize detector.
        Args:
            config: Settings configuration
        """
        self.config = config
        self.model = self._load_model()
        self.coco_to_target = config.get_coco_to_target_mapping()
        self.target_coco_ids = set(self.coco_to_target.keys())

    def _load_model(self) -> YOLO:
        """Load YOLO model."""
        try:
            model = YOLO(self.config.yolo_model)
            model.to("cpu")  # Use CPU by default, can be GPU if available
            return model
        except Exception as e:
            raise RuntimeError(f"Failed to load YOLO model: {e}")

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Run detection on frame.
        Args:
            frame: Input frame
        Returns:
            List of Detection objects for target classes only
        """
        detections: List[Detection] = []

        try:
            # Run inference
            results = self.model(
                frame,
                conf=self.config.yolo_confidence,
                iou=self.config.yolo_iou,
                verbose=False,
            )

            if results and results[0].boxes is not None:
                boxes = results[0].boxes

                for i in range(len(boxes)):
                    # Get class ID
                    class_id = int(boxes.cls[i])

                    # Filter to target classes only
                    if class_id not in self.target_coco_ids:
                        continue

                    # Get confidence
                    confidence = float(boxes.conf[i])

                    # Get bounding box (xyxy format)
                    box = boxes.xyxy[i]
                    x1, y1, x2, y2 = (
                        float(box[0]),
                        float(box[1]),
                        float(box[2]),
                        float(box[3]),
                    )
                    bbox = (x1, y1, x2, y2)

                    # Map COCO class to target class
                    class_name = self.coco_to_target.get(class_id, "unknown")

                    # Create detection
                    detection = Detection(
                        class_name=class_name,
                        confidence=confidence,
                        bbox=bbox,
                        track_id=None,
                    )
                    detections.append(detection)

        except Exception as e:
            print(f"Error during detection: {e}")

        return detections

    def get_model_info(self) -> dict:
        """Get information about loaded model."""
        return {
            "model": self.config.yolo_model,
            "task": self.model.task,
            "imgsz": self.model.imgsz,
        }
