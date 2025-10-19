"""
Accountant Agent - FastAPI Application
Production-grade microservice with modular architecture

KISS principle: Simple, clean FastAPI setup
DRY principle: Reusable shared components
Separation of Concerns: Infrastructure (this file) vs Business Logic (agent.py)
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.logger import logger

# Import shared components (middleware)
from shared.middleware import (
    add_security_headers,
    add_request_tracking,
    rate_limit_middleware,
    timeout_middleware,
    ALLOWED_ORIGINS
)

# Import shared health check route
from shared.routes import create_health_router

# Import agent-specific routes
from routes import allocation_router, reconciliation_router


# ============================================================================
# LIFECYCLE MANAGEMENT (Lifespan)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    Replaces deprecated @app.on_event()
    """
    # Startup
    logger.info("Accountant Agent starting up...")
    yield
    # Shutdown
    logger.info("Accountant Agent shutting down gracefully")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Accountant Agent",
    description="Production-grade allocation calculation agent for FlowShare",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") == "development" else None,
    redoc_url=None,
    lifespan=lifespan
)

# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# 1. CORS Protection (restrict to specific origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Added OPTIONS for preflight
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
    max_age=3600,
)

# 2. Response Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 3. Security Headers
app.middleware("http")(add_security_headers)

# 4. Request Tracking (request ID + timing)
app.middleware("http")(add_request_tracking)

# 5. Rate Limiting
app.middleware("http")(rate_limit_middleware)

# 6. Timeout Management
app.middleware("http")(timeout_middleware)

# ============================================================================
# ROUTES
# ============================================================================

# Health check routes (using shared router factory)
def get_accountant_agent():
    """Get accountant agent instance for health checks"""
    from agent import accountant_agent
    return accountant_agent

health_router = create_health_router(
    agent_name="Accountant Agent",
    version="1.0.0",
    agent_getter=get_accountant_agent
)
app.include_router(health_router)

# Agent routes
app.include_router(allocation_router)
app.include_router(reconciliation_router)

# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for uncaught exceptions

    Ensures no exception crashes the service
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.error(
        "Unhandled exception",
        request_id=request_id,
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": request_id
        }
    )

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8082,
        log_level="info",
        access_log=True,
        timeout_keep_alive=65
    )
