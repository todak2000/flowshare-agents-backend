"""Email templates for FlowShare notifications"""
from .email_template import (
    get_email_template,
    format_reconciliation_email,
    format_ai_reconciliation_report,
    format_reconciliation_pdf_email,
    format_audit_alert_email,
    format_generic_notification,
    format_markdown_for_email
)

__all__ = [
    'get_email_template',
    'format_reconciliation_email',
    'format_ai_reconciliation_report',
    'format_reconciliation_pdf_email',
    'format_audit_alert_email',
    'format_generic_notification',
    'format_markdown_for_email'
]
