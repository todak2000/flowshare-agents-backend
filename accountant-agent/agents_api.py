"""
Helper functions to call other agents
"""
import httpx
from typing import Dict, Any
from shared.logger import logger
from shared.config import config

COMMUNICATOR_URL = config.COMMUNICATOR_AGENT_URL or 'http://localhost:8083'

# Log the URL being used on module load
logger.info(f"Communicator Agent URL configured: {COMMUNICATOR_URL}")


async def send_notification_to_communicator(
    notification_id: str,
    recipient: str,
    subject: str,
    body: str,
    reconciliation_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send notification request to Communicator Agent

    Args:
        notification_id: Unique notification ID
        recipient: Email recipient
        subject: Email subject
        body: Email body
        reconciliation_data: Reconciliation data for email template

    Returns:
        Response from Communicator Agent
    """
    notify_url = f"{COMMUNICATOR_URL}/notify"

    try:
        logger.info(
            "Calling Communicator Agent",
            url=notify_url,
            recipient=recipient,
            subject=subject
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                notify_url,
                json={
                    "notification_id": notification_id,
                    "notification_data": {
                        "type": "email",
                        "recipient": recipient,
                        "subject": subject,
                        "body": body,
                        "metadata": {
                            "reconciliation_data": reconciliation_data
                        }
                    }
                }
            )

            if not response.is_success:
                logger.error(
                    f"Communicator Agent error: {response.status_code}",
                    url=notify_url,
                    response_text=response.text
                )
                return {"success": False, "error": response.text}

            data = response.json()
            logger.info("Communicator Agent responded successfully", recipient=recipient)
            return data

    except Exception as e:
        logger.error(
            f"Failed to call Communicator Agent: {e}",
            url=notify_url,
            error_type=type(e).__name__
        )
        return {"success": False, "error": str(e)}
