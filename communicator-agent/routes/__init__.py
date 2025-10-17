"""
Routes Package
Exports all route modules for the Communicator Agent
"""
from .notifications import router as notification_router

__all__ = ['notification_router']
