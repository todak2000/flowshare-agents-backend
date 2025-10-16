"""
Validation Routes
Handles production entry validation requests
KISS principle: Validation endpoint only
"""
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field, validator
from typing import Dict, Any
import asyncio
import sys
import os

# Add parent directory to path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent import auditor_agent
from shared.logger import logger

router = APIRouter(tags=["Validation"])


class ValidationRequest(BaseModel):
    """Request payload for validation"""
    entry_id: str = Field(..., min_length=1, max_length=100, description="Production entry ID")
    entry_data: Dict[str, Any] = Field(..., description="Production entry data")

    @validator('entry_id')
    def validate_entry_id(cls, v):
        """
        Sanitize entry ID to prevent injection attacks

        Checks for dangerous characters that could be used in:
        - SQL injection
        - XSS attacks
        - Command injection
        """
        if not v or not v.strip():
            raise ValueError("entry_id cannot be empty")

        # Check for dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$']
        for char in dangerous_chars:
            if char in v:
                raise ValueError(f"entry_id contains invalid character: {char}")

        return v.strip()


@router.post("/validate")
async def validate_entry(request: ValidationRequest, req: Request):
    """
    Validate a production entry

    Security:
    - CORS-restricted to allowed origins
    - Rate-limited to prevent abuse
    - Input sanitized and validated

    Performance:
    - Timeout-enforced (25 seconds)
    - Response compressed (if >1KB)

    Args:
        request: Validation request with entry_id and entry_data
        req: FastAPI request object (for request_id)

    Returns:
        Validation result with status, flags, and confidence score

    Raises:
        400 Bad Request: Invalid input data
        500 Internal Server Error: Validation failed
        504 Gateway Timeout: Validation took too long
    """
    request_id = getattr(req.state, 'request_id', 'unknown')

    try:
        logger.info(
            "Validation request received",
            request_id=request_id,
            entry_id=request.entry_id
        )

        # Prepare entry data
        entry_data = request.entry_data.copy()
        entry_data['id'] = request.entry_id

        # Validate with timeout
        try:
            result = await asyncio.wait_for(
                auditor_agent.validate_entry(entry_data),
                timeout=25.0  # Leave 5s buffer for middleware timeout
            )
        except asyncio.TimeoutError:
            logger.error("Validation timeout", request_id=request_id, entry_id=request.entry_id)
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Validation process timed out"
            )

        response_data = {
            "success": True,
            "entry_id": request.entry_id,
            "status": result.status,
            "flagged": result.flagged,
            "confidence_score": result.confidence_score,
            "issues_count": len(result.issues),
            "timestamp": result.timestamp,
            "request_id": request_id
        }

        logger.info(
            "Validation completed successfully",
            request_id=request_id,
            entry_id=request.entry_id,
            status=result.status,
            flagged=result.flagged
        )

        return response_data

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(
            "Invalid request data",
            request_id=request_id,
            entry_id=request.entry_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        logger.error(
            "Validation failed",
            request_id=request_id,
            entry_id=request.entry_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Check logs for details."
        )
