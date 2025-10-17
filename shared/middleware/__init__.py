"""
Shared middleware for all agents
Provides security, tracking, rate limiting, and timeout functionality
"""
from .security import ALLOWED_ORIGINS, add_security_headers
from .tracking import add_request_tracking
from .rate_limiting import rate_limit_middleware, RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW
from .timeout import timeout_middleware, REQUEST_TIMEOUT

__all__ = [
    "ALLOWED_ORIGINS",
    "add_security_headers",
    "add_request_tracking",
    "rate_limit_middleware",
    "RATE_LIMIT_REQUESTS",
    "RATE_LIMIT_WINDOW",
    "timeout_middleware",
    "REQUEST_TIMEOUT",
]
