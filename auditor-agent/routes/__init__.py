"""
Routes module for Auditor Agent API endpoints
"""
from .health import router as health_router
from .validation import router as validation_router

__all__ = ["health_router", "validation_router"]
