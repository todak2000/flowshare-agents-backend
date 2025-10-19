"""
Helper functions to call other agents
"""
import os
import httpx
from typing import Dict, Any
from shared.logger import logger

COMMUNICATOR_URL = os.getenv('COMMUNICATOR_AGENT_URL', 'http://localhost:8083')


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
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{COMMUNICATOR_URL}/notify",
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
                    response_text=response.text
                )
                return {"success": False, "error": response.text}

            data = response.json()
            return data

    except Exception as e:
        logger.error(f"Failed to call Communicator Agent: {e}")
        return {"success": False, "error": str(e)}
