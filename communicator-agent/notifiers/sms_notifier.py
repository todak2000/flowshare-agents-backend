"""
SMS Notifier
Sends SMS notifications using Twilio or other SMS service
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.logger import logger
from typing import Dict, Any, Optional


class SMSNotifier:
    """
    SMS notification sender

    Supports:
    - Twilio SMS delivery
    - International phone numbers

    TODO: Add support for other SMS providers (AWS SNS, Vonage, etc.)
    """

    def __init__(self):
        """Initialize SMS notifier with Twilio configuration"""
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER', '')

        # For development/testing, allow mock mode
        self.mock_mode = os.getenv('MOCK_SMS', 'false').lower() == 'true'

        logger.info(
            "SMSNotifier initialized",
            has_credentials=bool(self.twilio_account_sid and self.twilio_auth_token),
            mock_mode=self.mock_mode
        )

    async def send(
        self,
        phone_number: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send SMS notification

        Args:
            phone_number: Recipient phone number (E.164 format: +1234567890)
            message: SMS message body (max 160 characters recommended)
            metadata: Optional metadata

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            logger.info(
                "Sending SMS notification",
                phone_number=phone_number,
                message_length=len(message),
                mock_mode=self.mock_mode
            )

            # Mock mode for testing (doesn't actually send SMS)
            if self.mock_mode:
                logger.info("Mock SMS sent", phone_number=phone_number)
                return True

            # Validate Twilio credentials
            if not self.twilio_account_sid or not self.twilio_auth_token:
                logger.error("Twilio credentials not configured")
                return False

            # Validate phone number format (basic validation)
            if not phone_number.startswith('+'):
                logger.error("Invalid phone number format (must start with +)", phone_number=phone_number)
                return False

            # TODO: Integrate with Twilio SDK
            # from twilio.rest import Client
            # client = Client(self.twilio_account_sid, self.twilio_auth_token)
            # message = client.messages.create(
            #     body=message,
            #     from_=self.twilio_phone_number,
            #     to=phone_number
            # )

            logger.warning(
                "SMS sending not fully implemented (Twilio SDK required)",
                phone_number=phone_number
            )
            return False

        except Exception as e:
            logger.error(
                "SMS send failed",
                phone_number=phone_number,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
