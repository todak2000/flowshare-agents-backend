"""
Security Middleware
Handles CORS configuration and security headers
KISS principle: Security concerns only
"""
from fastapi import Request

# CORS - Restrict to specific origins
ALLOWED_ORIGINS = [
    "https://flowshare-197665497260.europe-west1.run.app",
    "https://communicator-agent-g5zmzlktoa-ew.a.run.app",
    "https://accountant-agent-g5zmzlktoa-ew.a.run.app",
    "https://auditor-agent-g5zmzlktoa-ew.a.run.app",
    "http://localhost:3000",
    "http://localhost:3001",  # For local testing
]


async def add_security_headers(request: Request, call_next):
    """
    Add security headers to all responses

    Headers added:
    - X-Content-Type-Options: Prevents MIME sniffing
    - X-Frame-Options: Prevents clickjacking
    - X-XSS-Protection: Enables XSS filter
    - Strict-Transport-Security: Enforces HTTPS
    - Content-Security-Policy: Restricts resource loading
    - Referrer-Policy: Controls referrer information

    Args:
        request: Incoming request
        call_next: Next middleware/handler

    Returns:
        Response with security headers
    """
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response
