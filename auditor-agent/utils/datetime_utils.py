"""
Datetime utilities
Provides timezone-aware datetime functions
"""
from datetime import datetime, timezone


def utc_now() -> datetime:
    """
    Get current UTC time as timezone-aware datetime

    Replaces deprecated datetime.utcnow() with timezone-aware alternative

    Returns:
        Timezone-aware datetime in UTC
    """
    return datetime.now(timezone.utc)
