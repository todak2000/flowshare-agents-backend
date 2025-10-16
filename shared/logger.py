"""
Structured logging for all agents
"""
import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict


def utc_now() -> datetime:
    """Get timezone-aware UTC datetime"""
    return datetime.now(timezone.utc)


class StructuredLogger:
    """JSON structured logger for Cloud Logging"""

    def __init__(self, name: str = "agent"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Create console handler with JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(self.JsonFormatter())
        self.logger.addHandler(handler)

    class JsonFormatter(logging.Formatter):
        """Format logs as JSON for Cloud Logging"""

        def format(self, record: logging.LogRecord) -> str:
            log_data = {
                "timestamp": utc_now().isoformat(),
                "severity": record.levelname,
                "message": record.getMessage(),
                "logger": record.name,
            }

            # Add extra fields if present
            if hasattr(record, 'extra_fields'):
                log_data.update(record.extra_fields)

            return json.dumps(log_data)

    def info(self, message: str, **kwargs):
        """Log info message"""
        extra = {'extra_fields': kwargs} if kwargs else {}
        self.logger.info(message, extra=extra)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        extra = {'extra_fields': kwargs} if kwargs else {}
        self.logger.warning(message, extra=extra)

    def error(self, message: str, **kwargs):
        """Log error message"""
        extra = {'extra_fields': kwargs} if kwargs else {}
        self.logger.error(message, extra=extra)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        extra = {'extra_fields': kwargs} if kwargs else {}
        self.logger.debug(message, extra=extra)


# Singleton instance
logger = StructuredLogger()
