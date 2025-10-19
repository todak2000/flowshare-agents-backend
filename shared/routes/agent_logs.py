"""
Agent Logs API Routes
Fetch agent activity logs with pagination
"""
from fastapi import APIRouter, Query
from typing import Dict, Any
from ..firestore_client import firestore_client
from ..config import config
from ..logger import logger

router = APIRouter(prefix="/agent-logs", tags=["agent-logs"])


@router.get("")
async def get_agent_logs(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(12, ge=1, le=100, description="Items per page")
) -> Dict[str, Any]:
    """
    Get agent activity logs with pagination

    Returns:
        Paginated agent logs with metadata
    """
    try:
        result = firestore_client.query_documents_paginated(
            collection=config.COLLECTION_AGENT_LOGS,
            page=page,
            page_size=page_size,
            order_by='timestamp',
            order_direction='DESCENDING'
        )

        logger.info(
            f"Retrieved agent logs page {page}",
            total=result['total'],
            returned=len(result['data'])
        )

        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error fetching agent logs: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
            "has_next": False,
            "has_prev": False
        }
