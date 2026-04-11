"""
Tests for configuration module.
"""

import os
import pytest
from pathlib import Path

from app.config import Settings, load_config


class TestConfigLoading:
    """Test configuration loading from environment."""

    def test_default_config(self):
        """Test loading default configuration."""
        config = Settings()
        assert config.vision_source == "samples/videos/demo.mp4"
        assert config.vision_camera_id == "1"
        assert config.yolo_model == "yolov8n.pt"
        assert config.yolo_confidence == 0.35
        assert config.yolo_iou == 0.45

    def test_config_from_env(self, monkeypatch):
        """Test loading configuration from environment variables."""
        monkeypatch.setenv("VISION_SOURCE", "rtsp://192.168.1.100:554/stream")
        monkeypatch.setenv("VISION_CAMERA_ID", "camera-01")
        monkeypatch.setenv("YOLO_CONFIDENCE", "0.5")

        config = Settings()
        assert config.vision_source == "rtsp://192.168.1.100:554/stream"
        assert config.vision_camera_id == "camera-01"
        assert config.yolo_confidence == 0.5

    def test_invalid_confidence_threshold(self):
        """Test validation of confidence threshold."""
        with pytest.raises(ValueError):
            Settings(yolo_confidence=1.5)

        with pytest.raises(ValueError):
            Settings(yolo_confidence=-0.1)

    def test_invalid_iou_threshold(self):
        """Test validation of IOU threshold."""
        with pytest.raises(ValueError):
            Settings(yolo_iou=1.5)

        with pytest.raises(ValueError):
            Settings(yolo_iou=-0.1)


class TestCocoClassMapping:
    """Test COCO to target class mapping."""

    def test_coco_to_target_mapping(self):
        """Test COCO class ID to target class name mapping."""
        config = Settings()
        mapping = config.get_coco_to_target_mapping()

        assert mapping[0] == "person"
        assert mapping[2] == "car"
        assert mapping[3] == "motorcycle"
        assert mapping[5] == "bus"
        assert mapping[7] == "truck"

    def test_target_classes(self):
        """Test getting target class list."""
        config = Settings()
        classes = config.get_target_classes()

        assert "person" in classes
        assert "car" in classes
        assert "motorcycle" in classes
        assert "bus" in classes
        assert "truck" in classes

    def test_coco_ids(self):
        """Test getting COCO class IDs."""
        config = Settings()
        coco_ids = config.get_coco_ids()

        assert 0 in coco_ids
        assert 2 in coco_ids
        assert 3 in coco_ids
        assert 5 in coco_ids
        assert 7 in coco_ids


class TestZonePointParsing:
    """Test zone polygon point parsing."""

    def test_valid_zone_points(self):
        """Test parsing valid zone points."""
        config = Settings(zone_points="0.2,0.3,0.8,0.3,0.8,0.9,0.2,0.9")
        points = config.parse_zone_points()

        assert len(points) == 4
        assert points[0] == (0.2, 0.3)
        assert points[1] == (0.8, 0.3)
        assert points[2] == (0.8, 0.9)
        assert points[3] == (0.2, 0.9)

    def test_zone_points_with_spaces(self):
        """Test parsing zone points with spaces."""
        config = Settings(zone_points="0.2, 0.3, 0.8, 0.3, 0.8, 0.9, 0.2, 0.9")
        points = config.parse_zone_points()

        assert len(points) == 4
        assert points[0] == (0.2, 0.3)

    def test_invalid_zone_points_count(self):
        """Test validation of zone points count."""
        with pytest.raises(ValueError):
            # Only 2 points (4 coordinates, need at least 6)
            config = Settings(zone_points="0.2,0.3,0.8,0.3")
            config.parse_zone_points()

    def test_invalid_zone_points_range(self):
        """Test validation of zone points range."""
        with pytest.raises(ValueError):
            # Point outside 0-1 range
            config = Settings(zone_points="0.2,0.3,1.5,0.3,0.8,0.9")
            config.parse_zone_points()

    def test_minimum_zone_points(self):
        """Test minimum valid zone (3 points)."""
        config = Settings(zone_points="0.0,0.0,1.0,0.0,0.5,1.0")
        points = config.parse_zone_points()

        assert len(points) == 3
        assert points[0] == (0.0, 0.0)
        assert points[1] == (1.0, 0.0)
        assert points[2] == (0.5, 1.0)


class TestPublishInterval:
    """Test publish interval configuration."""

    def test_valid_publish_interval(self):
        """Test valid publish interval."""
        config = Settings(publish_interval=300)
        assert config.publish_interval == 300

    def test_invalid_publish_interval_too_small(self):
        """Test publish interval validation (minimum 10)."""
        with pytest.raises(ValueError):
            Settings(publish_interval=5)

    def test_valid_line_y_ratio(self):
        """Test valid line Y ratio."""
        config = Settings(line_y_ratio=0.6)
        assert config.line_y_ratio == 0.6

    def test_invalid_line_y_ratio(self):
        """Test line Y ratio validation."""
        with pytest.raises(ValueError):
            Settings(line_y_ratio=1.5)
