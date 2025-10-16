"""
Health Check Routes
Provides health status and dependency validation
KISS principle: Health checking only
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from utils import utc_now

router = APIRouter(tags=["Health"])


@router.get("/")
async def root():
    """Root endpoint - basic service information"""
    return {
        "agent": "Auditor Agent",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": utc_now().isoformat()
    }


@router.get("/health")
async def health_check():
    """
    Comprehensive health check with dependency validation

    Checks:
    - Firestore connectivity
    - Gemini API availability
    - Agent initialization

    Returns:
        200 OK: All checks passed
        503 Service Unavailable: One or more checks failed
    """
    health_status = {
        "status": "healthy",
        "timestamp": utc_now().isoformat(),
        "checks": {}
    }

    # Check Firestore connectivity
    try:
        from shared.firestore_client import firestore_client
        test_doc = firestore_client.db.collection("_health_check").document("test")
        test_doc.set({"timestamp": utc_now().isoformat()}, merge=True)
        health_status["checks"]["firestore"] = "ok"
    except Exception as e:
        health_status["checks"]["firestore"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check Gemini API availability
    try:
        from shared.gemini_client import gemini_client
        if gemini_client.client:
            health_status["checks"]["gemini"] = "ok"
        else:
            health_status["checks"]["gemini"] = "error: client not initialized"
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["gemini"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check agent status
    try:
        from agent import auditor_agent
        if auditor_agent:
            health_status["checks"]["agent"] = "ok"
        else:
            health_status["checks"]["agent"] = "error: agent not initialized"
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["agent"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    status_code = status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(content=health_status, status_code=status_code)
