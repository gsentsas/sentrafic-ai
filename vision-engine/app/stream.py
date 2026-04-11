"""
Video stream handling for local files and RTSP cameras.
"""

import cv2
import time
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class VideoStream:
    """
    Handles reading from video files and RTSP streams.
    Supports reconnection for network streams.
    """

    def __init__(self, source: str, rtsp_timeout: float = 10.0):
        """
        Initialize video stream.
        Args:
            source: File path or RTSP URL
            rtsp_timeout: Connection timeout for RTSP (seconds)
        """
        self.source = source
        self.rtsp_timeout = rtsp_timeout
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_rtsp = source.startswith("rtsp://") or source.startswith("rtsp+tcp://")
        self.retry_count = 0
        self.max_retries = 5
        self.retry_delay = 2.0

    def open(self) -> bool:
        """
        Open video stream.
        Returns:
            True if successful
        """
        try:
            self.cap = cv2.VideoCapture(self.source)

            if self.is_rtsp:
                # Set RTSP-specific properties
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.cap.set(cv2.CAP_PROP_CONNECT_TIMEOUT, int(self.rtsp_timeout * 1000))

            # Test if stream is readable
            ret, _ = self.cap.read()
            if not ret:
                self.cap.release()
                self.cap = None
                logger.error(f"Failed to open stream: {self.source}")
                return False

            logger.info(f"Successfully opened stream: {self.source}")
            self.retry_count = 0
            return True

        except Exception as e:
            logger.error(f"Error opening stream {self.source}: {e}")
            if self.cap:
                self.cap.release()
            self.cap = None
            return False

    def read(self) -> Tuple[bool, Optional]:
        """
        Read next frame.
        Returns:
            Tuple of (success, frame)
        """
        if self.cap is None:
            return False, None

        try:
            ret, frame = self.cap.read()

            if not ret:
                if self.is_rtsp and self.retry_count < self.max_retries:
                    logger.warning(
                        f"RTSP stream error, retrying... (attempt {self.retry_count + 1}/{self.max_retries})"
                    )
                    self.retry_count += 1
                    time.sleep(self.retry_delay)
                    self.close()
                    self.open()
                    return self.read()

                return False, None

            self.retry_count = 0
            return True, frame

        except Exception as e:
            logger.error(f"Error reading frame: {e}")
            return False, None

    def is_opened(self) -> bool:
        """Check if stream is open."""
        return self.cap is not None and self.cap.isOpened()

    def close(self):
        """Close stream."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def release(self):
        """Release resources (alias for close)."""
        self.close()

    def get_fps(self) -> float:
        """Get frames per second of stream."""
        if self.cap is None:
            return 0.0
        return self.cap.get(cv2.CAP_PROP_FPS)

    def get_frame_size(self) -> Tuple[int, int]:
        """Get frame dimensions (width, height)."""
        if self.cap is None:
            return (0, 0)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)

    def get_frame_count(self) -> int:
        """Get total frame count (0 if unknown)."""
        if self.cap is None:
            return 0
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def get_position(self) -> int:
        """Get current frame position."""
        if self.cap is None:
            return 0
        return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
