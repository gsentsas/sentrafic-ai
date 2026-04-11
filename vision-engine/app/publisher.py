"""
Backend API publisher for traffic metrics.
"""

import requests
import time
import json
import logging
from typing import Optional, List
from datetime import datetime
from queue import Queue

from app.models import AggregateResult

logger = logging.getLogger(__name__)


class ResultPublisher:
    """
    Publishes aggregated traffic metrics to backend API.
    Handles retry logic and queuing for resilience.
    """

    def __init__(
        self,
        backend_url: str,
        api_key: str,
        camera_id: str,
        max_queue_size: int = 100,
    ):
        """
        Initialize publisher.
        Args:
            backend_url: Base URL of backend API
            api_key: API authentication key
            camera_id: Camera identifier
            max_queue_size: Maximum pending messages to queue
        """
        self.backend_url = backend_url.rstrip("/")
        self.api_key = api_key
        self.camera_id = camera_id
        self.endpoint = f"{self.backend_url}/api/ingest/events"
        self.max_queue_size = max_queue_size
        self.queue: Queue = Queue(maxsize=max_queue_size)
        self.max_retries = 3
        self.retry_delays = [1.0, 2.0, 4.0]  # Exponential backoff
        self.published_count = 0
        self.failed_count = 0

    def publish(self, result: AggregateResult) -> bool:
        """
        Publish aggregated result to backend.
        Args:
            result: AggregateResult to publish
        Returns:
            True if successful (or queued)
        """
        try:
            # Backend expects IngestBatch format: {"events": [event1, ...]}
            event_payload = result.to_json_payload()
            batch_payload = {"events": [event_payload]}
            return self._send_with_retry(batch_payload)
        except Exception as e:
            logger.error(f"Error publishing result: {e}")
            self.failed_count += 1
            return False

    def _send_with_retry(self, payload: dict) -> bool:
        """
        Send payload with retry logic.
        Args:
            payload: JSON payload to send
        Returns:
            True if successful
        """
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.endpoint,
                    json=payload,
                    headers=headers,
                    timeout=10.0,
                )

                if response.status_code in (200, 201):
                    logger.info(
                        f"Successfully published to {self.endpoint}: "
                        f"{response.status_code}"
                    )
                    self.published_count += 1
                    return True

                elif response.status_code >= 500:
                    # Server error, retry
                    logger.warning(
                        f"Server error {response.status_code}, retrying... "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delays[attempt])
                    continue

                else:
                    # Client error, don't retry
                    logger.error(
                        f"Client error {response.status_code}: {response.text}"
                    )
                    self.failed_count += 1
                    return False

            except requests.exceptions.Timeout:
                logger.warning(
                    f"Request timeout, retrying... "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delays[attempt])
                continue

            except requests.exceptions.ConnectionError:
                logger.warning(
                    f"Connection error, retrying... "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delays[attempt])
                continue

            except Exception as e:
                logger.error(f"Error sending request: {e}")
                self.failed_count += 1
                return False

        # All retries failed
        logger.error(
            f"Failed to publish after {self.max_retries} attempts, queuing for later"
        )
        self._queue_result(payload)
        return False

    def _queue_result(self, payload: dict) -> bool:
        """
        Queue result for later publishing.
        Args:
            payload: JSON payload to queue
        Returns:
            True if queued successfully
        """
        try:
            if self.queue.full():
                logger.warning("Publisher queue is full, dropping oldest message")
                try:
                    self.queue.get_nowait()
                except:
                    pass

            self.queue.put(payload, block=False)
            logger.info(f"Queued result for later publishing (queue size: {self.queue.qsize()})")
            return True
        except Exception as e:
            logger.error(f"Error queuing result: {e}")
            return False

    def flush_queue(self) -> int:
        """
        Attempt to publish all queued results.
        Returns:
            Number of successful publishes
        """
        success_count = 0

        while not self.queue.empty():
            try:
                payload = self.queue.get_nowait()
                if self._send_with_retry(payload):
                    success_count += 1
            except Exception as e:
                logger.error(f"Error flushing queue: {e}")

        return success_count

    def get_stats(self) -> dict:
        """Get publisher statistics."""
        return {
            "published": self.published_count,
            "failed": self.failed_count,
            "queued": self.queue.qsize(),
            "endpoint": self.endpoint,
        }

    def reset_stats(self):
        """Reset statistics."""
        self.published_count = 0
        self.failed_count = 0


class MockPublisher(ResultPublisher):
    """
    Mock publisher for testing (logs instead of sending).
    """

    def _send_with_retry(self, payload: dict) -> bool:
        """Log instead of sending."""
        logger.info(f"MOCK: Publishing payload: {json.dumps(payload, indent=2)}")
        self.published_count += 1
        return True
