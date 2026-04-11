"""
Configuration management for the vision engine.
Handles environment variables and derived settings.
"""

from typing import Dict, List, Tuple
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # Video source
    vision_source: str = Field(default="samples/videos/demo.mp4")
    vision_camera_id: str = Field(default="1")

    # YOLO model configuration
    yolo_model: str = Field(default="yolov8n.pt")
    yolo_confidence: float = Field(default=0.35, ge=0.0, le=1.0)
    yolo_iou: float = Field(default=0.45, ge=0.0, le=1.0)

    # Backend API configuration
    backend_url: str = Field(default="http://localhost:8000")
    backend_api_key: str = Field(default="vision-engine-key")

    # Aggregation and publishing
    publish_interval: int = Field(default=300, ge=10)

    # Detection zones and counters
    line_y_ratio: float = Field(default=0.6, ge=0.0, le=1.0)
    zone_points: str = Field(default="0.2,0.3,0.8,0.3,0.8,0.9,0.2,0.9")

    # Display and logging
    display_output: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @field_validator("yolo_confidence", "yolo_iou", "line_y_ratio")
    @classmethod
    def validate_ranges(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("Value must be between 0.0 and 1.0")
        return v

    def parse_zone_points(self) -> List[Tuple[float, float]]:
        """
        Parse zone points from comma-separated string.
        Format: x1,y1,x2,y2,x3,y3,...
        Returns list of (x, y) tuples as normalized coordinates (0-1).
        """
        try:
            coords = [float(x.strip()) for x in self.zone_points.split(",")]
            if len(coords) < 6 or len(coords) % 2 != 0:
                raise ValueError("Zone points must have at least 3 points (6 coordinates)")
            points = [(coords[i], coords[i + 1]) for i in range(0, len(coords), 2)]
            for x, y in points:
                if not (0.0 <= x <= 1.0) or not (0.0 <= y <= 1.0):
                    raise ValueError("All coordinates must be between 0 and 1")
            return points
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid zone points format: {e}")

    def get_coco_to_target_mapping(self) -> Dict[int, str]:
        """
        Map COCO class IDs to target classes.
        COCO dataset class indices:
        - 0: person
        - 2: car
        - 3: motorcycle
        - 5: bus
        - 7: truck
        """
        return {
            0: "person",
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck",
        }

    def get_target_classes(self) -> List[str]:
        """Get list of target class names."""
        return list(self.get_coco_to_target_mapping().values())

    def get_coco_ids(self) -> List[int]:
        """Get list of COCO class IDs we care about."""
        return list(self.get_coco_to_target_mapping().keys())


def load_config() -> Settings:
    """Load and validate configuration from environment."""
    return Settings()


# Global config instance
config = load_config()
