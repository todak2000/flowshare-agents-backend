"""
Notification Routes
Handles notification delivery requests
KISS principle: Send notification endpoint only
"""
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional
import asyncio
import sys
import os

# Add parent directory to path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent import communicator_agent
from shared.logger import logger

router = APIRouter(tags=["Notifications"])


class NotificationRequest(BaseModel):
    """Request payload for notification"""
    notification_id: str = Field(..., min_length=1, max_length=100, description="Notification ID")
    notification_data: Dict[str, Any] = Field(..., description="Notification data")

    @validator('notification_id')
    def validate_notification_id(cls, v):
        """
        Sanitize notification ID to prevent injection attacks

        Checks for dangerous characters that could be used in:
        - SQL injection
        - XSS attacks
        - Command injection
        """
        if not v or not v.strip():
            raise ValueError("notification_id cannot be empty")

        # Check for dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$']
        for char in dangerous_chars:
            if char in v:
                raise ValueError(f"notification_id contains invalid character: {char}")

        return v.strip()


@router.post("/notify")
async def send_notification(request: NotificationRequest, req: Request):
    """
    Send a notification

    Security:
    - CORS-restricted to allowed origins
    - Rate-limited to prevent abuse
    - Input sanitized and validated

    Performance:
    - Timeout-enforced (25 seconds)
    - Response compressed (if >1KB)

    Args:
        request: Notification request with notification_id and notification_data
        req: FastAPI request object (for request_id)

    Returns:
        Notification delivery result with status

    Raises:
        400 Bad Request: Invalid input data
        500 Internal Server Error: Notification delivery failed
        504 Gateway Timeout: Notification took too long
    """
    request_id = getattr(req.state, 'request_id', 'unknown')

    try:
        logger.info(
            "Notification request received",
            request_id=request_id,
            notification_id=request.notification_id
        )

        # Prepare notification data
        notification_data = request.notification_data.copy()
        notification_data['id'] = request.notification_id

        # Send notification with timeout
        try:
            result = await asyncio.wait_for(
                communicator_agent.send_notification(notification_data),
                timeout=25.0  # Leave 5s buffer for middleware timeout
            )
        except asyncio.TimeoutError:
            logger.error("Notification timeout", request_id=request_id, notification_id=request.notification_id)
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Notification delivery timed out"
            )

        response_data = {
            "success": result.status == "sent",
            "notification_id": request.notification_id,
            "status": result.status,
            "type": result.type,
            "recipient": result.recipient,
            "sent_at": result.sent_at,
            "error_message": result.error_message,
            "request_id": request_id
        }

        logger.info(
            "Notification completed",
            request_id=request_id,
            notification_id=request.notification_id,
            status=result.status,
            type=result.type
        )

        return response_data

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(
            "Invalid request data",
            request_id=request_id,
            notification_id=request.notification_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        logger.error(
            "Notification delivery failed",
            request_id=request_id,
            notification_id=request.notification_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Check logs for details."
        )
