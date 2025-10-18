"""
Communicator Agent - Notification Orchestrator

KISS principle: Simple orchestration of notification delivery
DRY principle: No repeated code, delegates to specialized notifiers
Single Responsibility: Coordinates notification workflow only
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.models import Notification, NotificationStatus, NotificationType
from shared.firestore_client import firestore_client
from shared.config import config
from shared.logger import logger
from shared.cache import SimpleCache
from shared.utils import utc_now
from typing import Dict, Any, Optional
import asyncio

# Import agent-specific notifiers
from notifiers import EmailNotifier, SMSNotifier, WebhookNotifier
from templates import format_ai_reconciliation_report
from utils import ai_report_generator


class CommunicatorAgent:
    """
    Agent 3: Notification Agent

    Orchestrates the notification workflow:
    1. Parse notification request
    2. Route to appropriate notifier
    3. Send notification
    4. Log activity
    5. Update Firestore

    Uses composition pattern with specialized notifiers
    """

    def __init__(self):
        """Initialize agent with modular notifiers"""
        self.name = "Communicator Agent"

        # Initialize components (Dependency Injection pattern)
        self._cache = SimpleCache(max_size=100)
        self._email_notifier = EmailNotifier()
        self._sms_notifier = SMSNotifier()
        self._webhook_notifier = WebhookNotifier()

        # Metrics
        self._notification_count = 0
        self._success_count = 0
        self._failure_count = 0

        logger.info(f"{self.name} initialized with modular notifiers")

    async def send_notification(self, notification_data: dict) -> Notification:
        """
        Main notification workflow

        Orchestrates:
        1. Data parsing and validation (Pydantic)
        2. Notifier routing (based on type)
        3. Notification delivery
        4. Status tracking
        5. Activity logging (Firestore)

        Args:
            notification_data: Notification document data

        Returns:
            Notification with delivery status
        """
        start_time = utc_now()
        self._notification_count += 1
        notification_id = notification_data.get('id', f'notif_{self._notification_count}')

        logger.info(
            "Starting notification delivery",
            notification_id=notification_id,
            notification_number=self._notification_count
        )

        try:
            # Step 1: Parse and validate with Pydantic
            notification = Notification(**notification_data)

            # Step 2: Route to appropriate notifier
            success, error_message = await self._route_notification(notification)

            # Step 3: Update status
            if success:
                notification.status = NotificationStatus.SENT
                notification.sent_at = utc_now().isoformat()
                self._success_count += 1
            else:
                notification.status = NotificationStatus.FAILED
                notification.error_message = error_message
                self._failure_count += 1

            # Step 4: Save results (async, non-blocking)
            execution_time = (utc_now() - start_time).total_seconds() * 1000
            await self._save_results(notification_id, notification, execution_time)

            logger.info(
                "Notification delivery complete",
                notification_id=notification_id,
                status=notification.status,
                notification_type=notification.type,
                execution_time_ms=round(execution_time, 2),
                success_rate=f"{self._success_count}/{self._notification_count}"
            )

            return notification

        except ValueError as e:
            logger.error("Invalid notification data", notification_id=notification_id, error=str(e))
            raise
        except Exception as e:
            logger.error(
                "Notification delivery failed",
                notification_id=notification_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise

    async def _route_notification(self, notification: Notification) -> tuple[bool, Optional[str]]:
        """
        Route notification to appropriate notifier

        Args:
            notification: Notification object

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if notification.type == NotificationType.EMAIL or notification.type == 'reconciliation_report':
                # Special handling for reconciliation reports
                if notification.type == 'reconciliation_report' or (
                    notification.metadata and 'reconciliation_data' in notification.metadata
                ):
                    logger.info("Generating AI-powered reconciliation report")

                    reconciliation_data = notification.metadata.get('reconciliation_data', {})

                    # Generate AI summary
                    ai_summary = await ai_report_generator.generate_reconciliation_summary(
                        reconciliation_data
                    )

                    # Format email with AI summary and full allocation details
                    body = format_ai_reconciliation_report(reconciliation_data, ai_summary)

                    success = await self._email_notifier.send(
                        recipient=notification.recipient,
                        subject=notification.subject or "FlowShare Reconciliation Report",
                        body=body,
                        metadata=notification.metadata
                    )
                else:
                    # Regular email
                    success = await self._email_notifier.send(
                        recipient=notification.recipient,
                        subject=notification.subject or "FlowShare Notification",
                        body=notification.body,
                        metadata=notification.metadata
                    )
            elif notification.type == NotificationType.SMS:
                success = await self._sms_notifier.send(
                    phone_number=notification.recipient,
                    message=notification.body,
                    metadata=notification.metadata
                )
            elif notification.type == NotificationType.WEBHOOK:
                success = await self._webhook_notifier.send(
                    url=notification.recipient,
                    payload=notification.metadata or {},
                    metadata=notification.metadata
                )
            else:
                logger.error("Unknown notification type", type=notification.type)
                return False, f"Unknown notification type: {notification.type}"

            if success:
                return True, None
            else:
                return False, "Notifier returned failure"

        except Exception as e:
            logger.error("Notifier error", error=str(e), type=notification.type)
            return False, str(e)

    async def _save_results(self, notification_id: str, notification: Notification, execution_time: float):
        """
        Save notification results to Firestore (async, non-blocking)

        Runs Firestore update and activity logging in parallel

        Args:
            notification_id: Notification identifier
            notification: Notification object
            execution_time: Execution time in milliseconds
        """
        try:
            await asyncio.gather(
                asyncio.to_thread(self._update_firestore, notification_id, notification),
                asyncio.to_thread(self._log_activity, notification_id, notification, execution_time)
            )
        except Exception as e:
            logger.error("Failed to save results", notification_id=notification_id, error=str(e))
            # Don't fail notification if saving fails

    def _update_firestore(self, notification_id: str, notification: Notification) -> None:
        """
        Update notification document in Firestore

        Args:
            notification_id: Notification identifier
            notification: Notification object
        """
        update_data = {
            'status': notification.status,
            'sent_at': notification.sent_at,
            'error_message': notification.error_message,
            'updated_at': utc_now().isoformat()
        }

        firestore_client.update_document(
            collection=config.COLLECTION_NOTIFICATIONS,
            doc_id=notification_id,
            data=update_data
        )

    def _log_activity(self, notification_id: str, notification: Notification, execution_time: float) -> None:
        """
        Log agent activity to Firestore

        Args:
            notification_id: Notification identifier
            notification: Notification object
            execution_time: Execution time in milliseconds
        """
        log_data = {
            'agent_name': self.name,
            'action': 'send_notification',
            'status': 'completed' if notification.status == NotificationStatus.SENT else 'failed',
            'input_data': {
                'notification_id': notification_id,
                'type': notification.type,
                'recipient': notification.recipient
            },
            'output_data': {
                'status': notification.status,
                'error': notification.error_message
            },
            'execution_time_ms': round(execution_time, 2),
            'timestamp': utc_now().isoformat()
        }

        firestore_client.log_agent_activity(log_data)

    # Public API for management and monitoring

    def clear_cache(self):
        """Clear cache (useful for testing or memory management)"""
        self._cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get agent statistics for monitoring

        Returns:
            Dictionary with agent statistics
        """
        return {
            "notification_count": self._notification_count,
            "success_count": self._success_count,
            "failure_count": self._failure_count,
            "success_rate": round((self._success_count / self._notification_count * 100), 2) if self._notification_count > 0 else 0,
            "cache_stats": self._cache.stats()
        }


# Singleton instance
communicator_agent = CommunicatorAgent()
