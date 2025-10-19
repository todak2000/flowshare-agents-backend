"""
Shared routes for all agents
Provides reusable health check functionality and agent logs
"""
from .health import create_health_router
from .agent_logs import router as agent_logs_router

__all__ = ["create_health_router", "agent_logs_router"]
