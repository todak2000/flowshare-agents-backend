"""
Request Tracking Middleware
Adds unique request IDs and timing information
KISS principle: Request tracking only
"""
from fastapi import Request
import uuid
import time
import sys
import os

# Add parent directory to path for shared module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.logger import logger


async def add_request_tracking(request: Request, call_next):
    """
    Add unique request ID and track processing time

    Adds:
    - X-Request-ID: Unique identifier for tracing
    - X-Process-Time: Time taken to process request

    Args:
        request: Incoming request
        call_next: Next middleware/handler

    Returns:
        Response with tracking headers
    """
    # Generate or reuse request ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    # Track processing time
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Convert to milliseconds

    # Add headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

    # Log request completion
    logger.info(
        "Request completed",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        process_time_ms=round(process_time, 2)
    )

    return response
