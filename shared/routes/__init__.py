"""
Shared routes for all agents
Provides reusable health check functionality
"""
from .health import create_health_router

__all__ = ["create_health_router"]
