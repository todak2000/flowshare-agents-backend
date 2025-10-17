"""
Timeout Middleware
Enforces request timeout to prevent resource exhaustion
KISS principle: Timeout handling only
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
import asyncio
import sys
import os

# Add parent directory to path for shared module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.logger import logger

# Timeout configuration
REQUEST_TIMEOUT = 30.0  # seconds


async def timeout_middleware(request: Request, call_next):
    """
    Enforce request timeout

    Prevents requests from hanging indefinitely and consuming resources.
    Returns 504 Gateway Timeout if request exceeds timeout.

    Args:
        request: Incoming request
        call_next: Next middleware/handler

    Returns:
        Response or 504 Gateway Timeout if timeout exceeded
    """
    try:
        return await asyncio.wait_for(
            call_next(request),
            timeout=REQUEST_TIMEOUT
        )
    except asyncio.TimeoutError:
        logger.error(f"Request timeout for {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "error": "Request timeout",
                "message": "Request took too long to process",
                "timeout_seconds": REQUEST_TIMEOUT
            }
        )
