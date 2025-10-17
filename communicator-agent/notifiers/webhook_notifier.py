"""
Webhook Notifier
Sends webhook notifications via HTTP POST
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.logger import logger
from typing import Dict, Any, Optional
import httpx
import asyncio


class WebhookNotifier:
    """
    Webhook notification sender

    Supports:
    - HTTP/HTTPS POST requests
    - JSON payload delivery
    - Retry logic with exponential backoff
    - Custom headers and authentication
    """

    def __init__(self):
        """Initialize webhook notifier"""
        self.timeout = int(os.getenv('WEBHOOK_TIMEOUT', '10'))  # 10 seconds default
        self.max_retries = int(os.getenv('WEBHOOK_MAX_RETRIES', '3'))

        # For development/testing, allow mock mode
        self.mock_mode = os.getenv('MOCK_WEBHOOK', 'false').lower() == 'true'

        logger.info(
            "WebhookNotifier initialized",
            timeout=self.timeout,
            max_retries=self.max_retries,
            mock_mode=self.mock_mode
        )

    async def send(
        self,
        url: str,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send webhook notification

        Args:
            url: Webhook URL (must be HTTPS in production)
            payload: JSON payload to send
            metadata: Optional metadata (e.g., custom headers, auth tokens)

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            logger.info(
                "Sending webhook notification",
                url=url,
                mock_mode=self.mock_mode
            )

            # Mock mode for testing
            if self.mock_mode:
                logger.info("Mock webhook sent", url=url)
                return True

            # Validate URL
            if not url.startswith('http://') and not url.startswith('https://'):
                logger.error("Invalid webhook URL", url=url)
                return False

            # Security: Warn if using HTTP instead of HTTPS in production
            if url.startswith('http://') and os.getenv('ENVIRONMENT') == 'production':
                logger.warning("Using insecure HTTP webhook in production", url=url)

            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'FlowShare-CommunicatorAgent/2.0'
            }

            # Add custom headers from metadata
            if metadata and 'headers' in metadata:
                headers.update(metadata['headers'])

            # Send webhook with retry logic
            for attempt in range(1, self.max_retries + 1):
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.post(
                            url,
                            json=payload,
                            headers=headers
                        )

                        # Check response status
                        if response.status_code >= 200 and response.status_code < 300:
                            logger.info(
                                "Webhook sent successfully",
                                url=url,
                                status_code=response.status_code,
                                attempt=attempt
                            )
                            return True
                        else:
                            logger.warning(
                                "Webhook returned non-success status",
                                url=url,
                                status_code=response.status_code,
                                attempt=attempt
                            )

                except httpx.TimeoutException:
                    logger.warning(
                        "Webhook timeout",
                        url=url,
                        attempt=attempt,
                        max_retries=self.max_retries
                    )
                except httpx.RequestError as e:
                    logger.warning(
                        "Webhook request error",
                        url=url,
                        attempt=attempt,
                        error=str(e)
                    )

                # Exponential backoff before retry
                if attempt < self.max_retries:
                    backoff_time = 2 ** attempt  # 2, 4, 8 seconds
                    logger.info(f"Retrying in {backoff_time} seconds...", attempt=attempt)
                    await asyncio.sleep(backoff_time)

            logger.error("Webhook failed after all retries", url=url, attempts=self.max_retries)
            return False

        except Exception as e:
            logger.error(
                "Webhook send failed",
                url=url,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
