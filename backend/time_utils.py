"""
Time utility functions for the SupplyLine MRO Suite application.

This module provides standardized time handling functions to ensure
consistent time management across the application.
"""

from datetime import UTC, datetime, timedelta


def get_utc_now() -> datetime:
    """
    Get the current UTC time as a timezone-aware datetime object.

    Returns:
        datetime: Current UTC time with timezone information
    """
    return datetime.now(UTC)


def get_utc_timestamp() -> datetime:
    """
    Get the current UTC timestamp as a naive datetime object.
    This is compatible with SQLAlchemy's default datetime handling.

    Returns:
        datetime: Current UTC time as a naive datetime object
    """
    # For consistency with the application's requirements to use local time,
    # we'll return the local time instead of UTC time
    return get_local_timestamp()


def get_local_timestamp() -> datetime:
    """
    Get the current local time as a naive datetime object.
    This is useful for displaying times in the local timezone.

    Returns:
        datetime: Current local time as a naive datetime object
    """
    return datetime.now()


def format_datetime(dt: datetime | None) -> str | None:
    """
    Format a datetime object to ISO 8601 format.

    Args:
        dt (datetime): The datetime object to format

    Returns:
        str: Formatted datetime string
    """
    if dt is None:
        return None

    # If the datetime is naive, assume it's UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    return dt.isoformat()


def parse_iso_datetime(dt_str: str) -> datetime | None:
    """
    Parse an ISO 8601 datetime string to a datetime object.

    Args:
        dt_str (str): The datetime string to parse

    Returns:
        datetime: Parsed datetime object with UTC timezone
    """
    if not dt_str:
        return None

    # Handle various formats
    try:
        # Try parsing with timezone info
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
    except ValueError:
        try:
            # Try parsing without timezone info (assume UTC)
            dt = datetime.fromisoformat(dt_str)
            dt = dt.replace(tzinfo=UTC)
        except ValueError:
            # Last resort, try a more flexible approach
            formats = [
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d"
            ]

            for fmt in formats:
                try:
                    dt = datetime.strptime(dt_str, fmt)
                    dt = dt.replace(tzinfo=UTC)
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(f"Could not parse datetime string: {dt_str}")

    return dt


def add_days(dt: datetime | None, days: int) -> datetime | None:
    """
    Add a specified number of days to a datetime object.

    Args:
        dt (datetime): The datetime object
        days (int): Number of days to add

    Returns:
        datetime: New datetime object with days added
    """
    if dt is None:
        return None

    return dt + timedelta(days=days)


def days_between(dt1: datetime | None, dt2: datetime | None = None) -> int | None:
    """
    Calculate the number of days between two datetime objects.
    If dt2 is not provided, uses the current UTC time.

    Args:
        dt1 (datetime): First datetime object
        dt2 (datetime, optional): Second datetime object

    Returns:
        int: Number of days between dt1 and dt2
    """
    if dt1 is None:
        return None

    if dt2 is None:
        dt2 = get_utc_timestamp()

    # Ensure both datetimes are naive for comparison
    if dt1.tzinfo is not None:
        dt1 = dt1.replace(tzinfo=None)

    if dt2.tzinfo is not None:
        dt2 = dt2.replace(tzinfo=None)

    # Set time to midnight for accurate day calculation
    dt1 = dt1.replace(hour=0, minute=0, second=0, microsecond=0)
    dt2 = dt2.replace(hour=0, minute=0, second=0, microsecond=0)

    delta = dt2 - dt1
    return delta.days
