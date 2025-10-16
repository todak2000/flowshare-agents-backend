"""
Auditor Agent - FastAPI Application
Receives HTTP requests from Cloud Function triggers
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import asyncio
from agent import auditor_agent
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.logger import logger

# Initialize FastAPI
app = FastAPI(
    title="Auditor Agent",
    description="Data validation agent for FlowShare",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ValidationRequest(BaseModel):
    """Request payload from Cloud Function"""
    entry_id: str
    entry_data: Dict[str, Any]


@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "agent": "Auditor Agent",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/validate")
async def validate_entry(request: ValidationRequest):
    """
    Validate a production entry
    Called by Cloud Function trigger
    """
    try:
        logger.info(f"Received validation request for entry: {request.entry_id}")

        # Add ID to entry data
        entry_data = request.entry_data
        entry_data['id'] = request.entry_id

        # Validate
        result = await auditor_agent.validate_entry(entry_data)

        return {
            "success": True,
            "entry_id": request.entry_id,
            "status": result.status,
            "flagged": result.flagged,
            "confidence_score": result.confidence_score,
            "issues_count": len(result.issues)
        }

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Kubernetes/Cloud Run health check"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
