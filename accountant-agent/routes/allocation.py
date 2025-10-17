"""
Allocation Routes
Handles terminal receipt allocation calculation requests
KISS principle: Calculate allocation endpoint only
"""
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field, validator
from typing import Dict, Any
import asyncio
import sys
import os

# Add parent directory to path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent import accountant_agent
from shared.logger import logger

router = APIRouter(tags=["Allocation"])


class AllocationRequest(BaseModel):
    """Request payload for allocation calculation"""
    receipt_id: str = Field(..., min_length=1, max_length=100, description="Terminal receipt ID")
    receipt_data: Dict[str, Any] = Field(..., description="Terminal receipt data")

    @validator('receipt_id')
    def validate_receipt_id(cls, v):
        """
        Sanitize receipt ID to prevent injection attacks

        Checks for dangerous characters that could be used in:
        - SQL injection
        - XSS attacks
        - Command injection
        """
        if not v or not v.strip():
            raise ValueError("receipt_id cannot be empty")

        # Check for dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$']
        for char in dangerous_chars:
            if char in v:
                raise ValueError(f"receipt_id contains invalid character: {char}")

        return v.strip()


@router.post("/calculate")
async def calculate_allocations(request: AllocationRequest, req: Request):
    """
    Calculate partner allocations for a terminal receipt

    Security:
    - CORS-restricted to allowed origins
    - Rate-limited to prevent abuse
    - Input sanitized and validated

    Performance:
    - Timeout-enforced (25 seconds)
    - Response compressed (if >1KB)

    Args:
        request: Allocation request with receipt_id and receipt_data
        req: FastAPI request object (for request_id)

    Returns:
        Allocation result with partner allocations and totals

    Raises:
        400 Bad Request: Invalid input data
        500 Internal Server Error: Calculation failed
        504 Gateway Timeout: Calculation took too long
    """
    request_id = getattr(req.state, 'request_id', 'unknown')

    try:
        logger.info(
            "Allocation request received",
            request_id=request_id,
            receipt_id=request.receipt_id
        )

        # Prepare receipt data
        receipt_data = request.receipt_data.copy()
        receipt_data['id'] = request.receipt_id

        # Calculate allocations with timeout
        try:
            result = await asyncio.wait_for(
                accountant_agent.calculate_allocation(receipt_data),
                timeout=25.0  # Leave 5s buffer for middleware timeout
            )
        except asyncio.TimeoutError:
            logger.error("Allocation calculation timeout", request_id=request_id, receipt_id=request.receipt_id)
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Allocation calculation timed out"
            )

        response_data = {
            "success": True,
            "receipt_id": request.receipt_id,
            "allocations": [allocation.dict() for allocation in result.allocations],
            "total_allocated": result.total_allocated,
            "timestamp": result.timestamp,
            "request_id": request_id
        }

        logger.info(
            "Allocation calculation completed successfully",
            request_id=request_id,
            receipt_id=request.receipt_id,
            allocations_count=len(result.allocations),
            total_allocated=result.total_allocated
        )

        return response_data

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(
            "Invalid request data",
            request_id=request_id,
            receipt_id=request.receipt_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        logger.error(
            "Allocation calculation failed",
            request_id=request_id,
            receipt_id=request.receipt_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Check logs for details."
        )
