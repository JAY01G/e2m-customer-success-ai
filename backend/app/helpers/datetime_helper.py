"""Datetime Conversion and Utility Helpers.

Provides timezone-aware UTC timestamps and ISO 8601 parsing/formatting utilities.
"""

from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    """Return current timezone-aware UTC datetime.

    Returns:
        datetime: Current datetime in timezone.utc.
    """
    return datetime.now(timezone.utc)


def format_iso(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime to standard ISO 8601 string.

    Args:
        dt: Optional datetime object.

    Returns:
        Optional[str]: ISO formatted string or None.
    """
    if not dt:
        return None
    return dt.isoformat()


def parse_iso(iso_str: str) -> datetime:
    """Parse ISO 8601 string into datetime object.

    Args:
        iso_str: ISO formatted timestamp string.

    Returns:
        datetime: Parsed datetime object.
    """
    return datetime.fromisoformat(iso_str)

