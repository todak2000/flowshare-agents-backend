"""
Reconciliation Routes
Handles monthly reconciliation requests
Triggers full month reconciliation and notifies Communicator Agent
"""
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime
import asyncio
import sys
import os

# Add parent directory to path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.logger import logger
from shared.firestore_client import firestore_client
from shared.config import config

router = APIRouter(tags=["Reconciliation"])


class ReconciliationRequest(BaseModel):
    """Request payload for monthly reconciliation"""
    start_date: str = Field(..., description="Start date (ISO format)")
    end_date: str = Field(..., description="End date (ISO format)")
    triggered_by: str = Field(..., description="User ID who triggered reconciliation")
    reconciliation_id: str = Field(..., description="Reconciliation document ID")


@router.post("/reconcile")
async def trigger_reconciliation(request: ReconciliationRequest, req: Request):
    """
    Trigger full month reconciliation

    This endpoint:
    1. Receives reconciliation parameters
    2. Reconciliation logic is already done by frontend
    3. Sends notification to Communicator Agent with results

    Args:
        request: Reconciliation request with date range and reconciliation_id
        req: FastAPI request object (for request_id)

    Returns:
        Success status with reconciliation_id

    Raises:
        400 Bad Request: Invalid input data
        500 Internal Server Error: Reconciliation failed
    """
    request_id = getattr(req.state, 'request_id', 'unknown')

    try:
        logger.info(
            "Reconciliation request received",
            request_id=request_id,
            reconciliation_id=request.reconciliation_id,
            start_date=request.start_date,
            end_date=request.end_date
        )

        # Get reconciliation data from Firestore
        reconciliation_doc = firestore_client.get_document(
            collection=config.COLLECTION_RECONCILIATIONS,
            doc_id=request.reconciliation_id
        )

        if not reconciliation_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reconciliation {request.reconciliation_id} not found"
            )

        # Get allocation results for this reconciliation
        allocations = firestore_client.query_documents(
            collection=config.COLLECTION_ALLOCATIONS,
            filters=[('reconciliation_id', '==', request.reconciliation_id)]
        )

        logger.info(
            f"Found {len(allocations)} allocations for reconciliation",
            reconciliation_id=request.reconciliation_id
        )

        # Send notification to Communicator Agent
        from agents_api import send_notification_to_communicator

        # Format period for subject line
        start_dt = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))
        period_month = start_dt.strftime('%B %Y')

        # Prepare reconciliation data for email
        reconciliation_data = {
            'reconciliation_id': request.reconciliation_id,
            'period_start': start_dt.strftime('%Y-%m-%d'),
            'period_end': end_dt.strftime('%Y-%m-%d'),
            'period_month': period_month,
            'allocations_count': len(allocations),
            'total_input_volume': reconciliation_doc.get('total_input_volume', 0),
            'terminal_volume': reconciliation_doc.get('total_terminal_volume', 0),
            'shrinkage_factor': reconciliation_doc.get('shrinkage_factor', 0),
            'partners': ', '.join(set(a.get('partner', '') for a in allocations)),
            'allocations': [
                {
                    'partner': a.get('partner', ''),
                    'input_volume': a.get('input_volume', 0),
                    'allocated_volume': a.get('allocated_volume', 0),
                    'volume_loss': a.get('volume_loss', 0),
                    'percentage': a.get('percentage', 0),
                }
                for a in allocations
            ],
        }

        # Get unique partners and collect stakeholder emails
        unique_partners = list(set(a.get('partner', '') for a in allocations))
        logger.info(f"Collecting stakeholder emails for {len(unique_partners)} partners")
        logger.info(f"Partners: {unique_partners}")

        # Collect all stakeholders
        stakeholder_emails = set()

        # ALWAYS include default admin email
        DEFAULT_ADMIN_EMAIL = "todak2000@gmail.com"
        stakeholder_emails.add(DEFAULT_ADMIN_EMAIL)
        logger.info(f"✅ Added default admin email: {DEFAULT_ADMIN_EMAIL}")

        # 1. Get all JV coordinators
        logger.info("Querying for JV coordinators from appUsers collection...")
        jv_coordinators = firestore_client.query_documents(
            collection='appUsers',
            filters=[('role', '==', 'jv_coordinator')]
        )
        jv_coordinator_emails = [u.get('email') for u in jv_coordinators if u.get('email')]
        stakeholder_emails.update(jv_coordinator_emails)
        logger.info(f"Found {len(jv_coordinators)} JV coordinators: {jv_coordinator_emails}")

        # 2. Get field operators and JV partners for each partner
        for partner_name in unique_partners:
            logger.info(f"Querying for field operators and JV partners for partner: {partner_name}")

            field_ops = firestore_client.query_documents(
                collection='appUsers',
                filters=[
                    ('role', '==', 'field_operator'),
                    ('company', '==', partner_name)
                ]
            )
            field_op_emails = [u.get('email') for u in field_ops if u.get('email')]
            logger.info(f"Found {len(field_ops)} field operators for {partner_name}: {field_op_emails}")

            jv_partners = firestore_client.query_documents(
                collection='appUsers',
                filters=[
                    ('role', '==', 'jv_partner'),
                    ('company', '==', partner_name)
                ]
            )
            jv_partner_emails = [u.get('email') for u in jv_partners if u.get('email')]
            logger.info(f"Found {len(jv_partners)} JV partners for {partner_name}: {jv_partner_emails}")

            stakeholder_emails.update(field_op_emails)
            stakeholder_emails.update(jv_partner_emails)

        logger.info(f"Total unique stakeholder emails collected (including admin): {len(stakeholder_emails)}")

        # Log all emails that will receive notifications
        logger.info(f"📧 STAKEHOLDER EMAILS TO NOTIFY ({len(stakeholder_emails)}):")
        for email in sorted(stakeholder_emails):
            logger.info(f"  - {email}")

        logger.info(f"Starting notification process for {len(stakeholder_emails)} stakeholders...")

        # Send notifications to all stakeholders
        notification_results = []
        for index, email in enumerate(stakeholder_emails):
            try:
                result = await send_notification_to_communicator(
                    notification_id=f"notif_{request.reconciliation_id}_{index}",
                    recipient=email,
                    subject=f"✅ {period_month} Reconciliation Report Available",
                    body=f"Reconciliation report for {period_month}",
                    reconciliation_data=reconciliation_data
                )
                notification_results.append({
                    'email': email,
                    'success': result.get('success', False)
                })
            except Exception as e:
                logger.error(f"Failed to send notification to {email}: {e}")
                notification_results.append({
                    'email': email,
                    'success': False,
                    'error': str(e)
                })

        successful_notifications = sum(1 for r in notification_results if r.get('success'))
        logger.info(
            f"Sent {successful_notifications}/{len(stakeholder_emails)} notifications successfully",
            reconciliation_id=request.reconciliation_id
        )

        return {
            "success": True,
            "reconciliation_id": request.reconciliation_id,
            "notifications_sent": successful_notifications,
            "total_stakeholders": len(stakeholder_emails),
            "request_id": request_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Reconciliation request failed",
            request_id=request_id,
            reconciliation_id=request.reconciliation_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reconciliation failed: {str(e)}"
        )
