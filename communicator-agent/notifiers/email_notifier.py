"""
Email Notifier
Sends email notifications using ZeptoMail API
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.logger import logger
from typing import Dict, Any, Optional
import httpx
from templates import get_email_template, format_generic_notification


class EmailNotifier:
    """
    Email notification sender using ZeptoMail API

    Supports:
    - ZeptoMail transactional email delivery
    - HTML and plain text emails
    - High deliverability rates

    API Documentation: https://www.zoho.com/zeptomail/help/api/
    """

    def __init__(self):
        """Initialize email notifier with ZeptoMail configuration"""
        self.zepto_token = os.getenv('ZEPTO_TOKEN', '')
        self.from_email = os.getenv('ZEPTO_FROM_EMAIL', 'noreply@futuxconsult.com')
        self.api_url = 'https://api.zeptomail.com/v1.1/email'

        # Always BCC admin on all emails
        self.admin_bcc = os.getenv('ADMIN_EMAIL', 'todak2000@gmail.com')

        # For development/testing, allow mock mode
        self.mock_mode = os.getenv('MOCK_EMAIL', 'false').lower() == 'true'

        logger.info(
            "EmailNotifier initialized with ZeptoMail",
            from_email=self.from_email,
            has_token=bool(self.zepto_token),
            mock_mode=self.mock_mode,
            admin_bcc=self.admin_bcc
        )

    async def send(
        self,
        recipient: str | list[str],
        subject: str,
        body: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send email notification via ZeptoMail API

        Args:
            recipient: Email address(es) of recipient(s) - single string or list
            subject: Email subject
            body: Email body (plain text or HTML)
            metadata: Optional metadata (e.g., cc, bcc, reply_to)

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            logger.info(
                "Sending email notification via ZeptoMail",
                recipient=recipient,
                subject=subject,
                mock_mode=self.mock_mode
            )

            # Mock mode for testing (doesn't actually send email)
            if self.mock_mode:
                logger.info("Mock email sent", recipient=recipient, subject=subject)
                return True

            # Validate ZeptoMail token
            if not self.zepto_token:
                logger.error("ZeptoMail token not configured")
                return False

            # Check if body is already a full HTML template
            is_full_html = '<html>' in body.lower() and '</html>' in body.lower()

            # If it's plain text or partial HTML, wrap it in professional template
            if not is_full_html:
                # Convert plain text to HTML paragraphs
                if '<' not in body:
                    # Plain text - convert to HTML
                    body_html = '<p>' + body.replace('\n\n', '</p><p>').replace('\n', '<br>') + '</p>'
                else:
                    # Partial HTML - use as is
                    body_html = body

                # Wrap in professional template
                body = format_generic_notification(subject, body_html)

            # Handle both single recipient (string) and multiple recipients (list)
            recipients_list = [recipient] if isinstance(recipient, str) else recipient

            # Prepare ZeptoMail payload
            payload = {
                "from": {
                    "address": self.from_email,
                    "name": "FlowShare Communication Agent"
                },
                "to": [
                    {
                        "email_address": {
                            "address": email
                        }
                    }
                    for email in recipients_list
                ],
                "subject": subject,
                "htmlbody": body  # Always send HTML now with professional template
            }

            # Add optional fields from metadata
            if metadata:
                if 'reply_to' in metadata:
                    payload["reply_to"] = [{"address": metadata['reply_to']}]
                if 'cc' in metadata:
                    payload["cc"] = [{"email_address": {"address": email}} for email in metadata['cc']]

            # Always BCC admin email on all notifications
            bcc_list = []
            if metadata and 'bcc' in metadata:
                bcc_list.extend(metadata['bcc'])

            # Add admin email if not already in recipients or BCC
            if self.admin_bcc and self.admin_bcc not in bcc_list and self.admin_bcc not in recipients_list:
                bcc_list.append(self.admin_bcc)

            if bcc_list:
                payload["bcc"] = [{"email_address": {"address": email}} for email in bcc_list]

            # Send email via ZeptoMail API
            headers = {
                'Authorization': self.zepto_token,
                'Content-Type': 'application/json'
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )

                if response.status_code == 201:
                    logger.info("Email sent successfully via ZeptoMail", recipient=recipient)
                    return True
                else:
                    logger.error(
                        "ZeptoMail API error",
                        recipient=recipient,
                        status_code=response.status_code,
                        response=response.text
                    )
                    return False

        except httpx.TimeoutException:
            logger.error("ZeptoMail API timeout", recipient=recipient)
            return False
        except httpx.RequestError as e:
            logger.error("ZeptoMail API request error", recipient=recipient, error=str(e))
            return False
        except Exception as e:
            logger.error(
                "Email send failed",
                recipient=recipient,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
