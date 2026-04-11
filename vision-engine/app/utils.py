"""
Utility functions for the vision engine.
Geometric calculations, logging, and helpers.
"""

import logging
import math
from typing import Tuple, List, Optional
from datetime import datetime


def get_center(bbox: Tuple[float, float, float, float]) -> Tuple[float, float]:
    """
    Get center point of bounding box.
    Args:
        bbox: (x1, y1, x2, y2)
    Returns:
        (center_x, center_y)
    """
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def bbox_area(bbox: Tuple[float, float, float, float]) -> float:
    """
    Calculate bounding box area.
    Args:
        bbox: (x1, y1, x2, y2)
    Returns:
        Area in square pixels
    """
    x1, y1, x2, y2 = bbox
    return max(0, (x2 - x1) * (y2 - y1))


def euclidean_distance(
    p1: Tuple[float, float], p2: Tuple[float, float]
) -> float:
    """
    Calculate Euclidean distance between two points.
    Args:
        p1: (x1, y1)
        p2: (x2, y2)
    Returns:
        Distance in pixels
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx * dx + dy * dy)


def point_in_polygon(
    point: Tuple[float, float], polygon: List[Tuple[float, float]]
) -> bool:
    """
    Check if point is inside polygon using ray casting algorithm.
    Args:
        point: (x, y)
        polygon: List of (x, y) vertices
    Returns:
        True if point is inside polygon
    """
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def line_crossed(
    prev_pos: Tuple[float, float],
    curr_pos: Tuple[float, float],
    line_y: float,
) -> bool:
    """
    Check if a trajectory crossed a horizontal line.
    Args:
        prev_pos: Previous (x, y) position
        curr_pos: Current (x, y) position
        line_y: Y-coordinate of the counting line
    Returns:
        True if line was crossed
    """
    if prev_pos is None or curr_pos is None:
        return False

    prev_y = prev_pos[1]
    curr_y = curr_pos[1]

    # Check if trajectory crossed the line
    return (prev_y < line_y <= curr_y) or (prev_y > line_y >= curr_y)


def get_crossing_direction(
    prev_pos: Tuple[float, float],
    curr_pos: Tuple[float, float],
    line_y: float,
) -> Optional[str]:
    """
    Determine direction of line crossing (up or down).
    Args:
        prev_pos: Previous (x, y) position
        curr_pos: Current (x, y) position
        line_y: Y-coordinate of the counting line
    Returns:
        "up" if moving upward, "down" if moving downward, None if no crossing
    """
    if not line_crossed(prev_pos, curr_pos, line_y):
        return None

    if prev_pos[1] < curr_pos[1]:
        return "down"
    else:
        return "up"


def calculate_congestion(occupancy: float, vehicle_count: int) -> str:
    """
    Classify traffic congestion level.
    Args:
        occupancy: Zone occupancy ratio (0-1)
        vehicle_count: Number of vehicles in zone
    Returns:
        Congestion level: "free", "moderate", "heavy", "blocked"
    """
    if occupancy < 0.2:
        return "free"
    elif occupancy < 0.5:
        return "moderate"
    elif occupancy < 0.8:
        return "heavy"
    else:
        return "blocked"


def format_timestamp() -> str:
    """
    Get current timestamp as ISO 8601 string.
    Returns:
        ISO formatted datetime string
    """
    return datetime.utcnow().isoformat() + "Z"


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Setup a logger with console handler.
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler
    handler = logging.StreamHandler()
    handler.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


def normalize_bbox(
    bbox: Tuple[float, float, float, float],
    frame_width: int,
    frame_height: int,
) -> Tuple[float, float, float, float]:
    """
    Convert pixel coordinates to normalized coordinates (0-1).
    Args:
        bbox: (x1, y1, x2, y2) in pixels
        frame_width: Frame width in pixels
        frame_height: Frame height in pixels
    Returns:
        (x1_norm, y1_norm, x2_norm, y2_norm) normalized to 0-1
    """
    x1, y1, x2, y2 = bbox
    return (
        x1 / frame_width,
        y1 / frame_height,
        x2 / frame_width,
        y2 / frame_height,
    )


def denormalize_bbox(
    bbox: Tuple[float, float, float, float],
    frame_width: int,
    frame_height: int,
) -> Tuple[int, int, int, int]:
    """
    Convert normalized coordinates to pixel coordinates.
    Args:
        bbox: (x1_norm, y1_norm, x2_norm, y2_norm) normalized to 0-1
        frame_width: Frame width in pixels
        frame_height: Frame height in pixels
    Returns:
        (x1, y1, x2, y2) in pixels
    """
    x1_norm, y1_norm, x2_norm, y2_norm = bbox
    return (
        int(x1_norm * frame_width),
        int(y1_norm * frame_height),
        int(x2_norm * frame_width),
        int(y2_norm * frame_height),
    )
