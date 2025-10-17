"""
Rate Limiting Middleware
Prevents API abuse with request rate limiting
KISS principle: Rate limiting only
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from collections import defaultdict
import time
import sys
import os

# Add parent directory to path for shared module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.logger import logger

# Rate limit configuration
RATE_LIMIT_REQUESTS = 100  # Maximum requests
RATE_LIMIT_WINDOW = 60  # Time window in seconds

# In-memory storage (use Redis for production multi-instance setup)
rate_limit_storage = defaultdict(list)


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limit requests based on IP address

    Configuration:
    - 100 requests per 60-second window per IP
    - Excludes health check endpoints

    Args:
        request: Incoming request
        call_next: Next middleware/handler

    Returns:
        Response or 429 Too Many Requests if limit exceeded
    """
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/", "/"]:
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()

    # Clean old requests outside the time window
    rate_limit_storage[client_ip] = [
        req_time for req_time in rate_limit_storage[client_ip]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]

    # Check rate limit
    if len(rate_limit_storage[client_ip]) >= RATE_LIMIT_REQUESTS:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": f"Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds",
                "retry_after": RATE_LIMIT_WINDOW
            }
        )

    # Add current request timestamp
    rate_limit_storage[client_ip].append(current_time)

    # Process request and add rate limit headers
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(
        RATE_LIMIT_REQUESTS - len(rate_limit_storage[client_ip])
    )

    return response
