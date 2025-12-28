"""Shared validators for Master Resume models."""

import re
from datetime import date
from urllib.parse import urlparse

from pydantic_core import PydanticCustomError


def validate_phone(value: str) -> str:
    """Validate phone number format.

    Accepts formats like:
    - +1 (555) 123-4567
    - 555-123-4567
    - +44 20 7123 4567

    Args:
        value: Phone number string

    Returns:
        Original phone number (validated)

    Raises:
        PydanticCustomError: If phone format is invalid
    """
    # Remove whitespace and common separators for validation
    cleaned = re.sub(r"[\s\-\(\)\.]", "", value)

    # Must be digits, optionally starting with +
    if not re.match(r"^\+?\d{7,15}$", cleaned):
        raise PydanticCustomError(
            "phone_format",
            "Invalid phone number format. Expected: +1 (555) 123-4567",
            {"value": value},
        )
    return value


def validate_linkedin_url(value: str) -> str:
    """Validate and normalize LinkedIn profile URL.

    Accepts:
    - linkedin.com/in/username
    - https://linkedin.com/in/username
    - www.linkedin.com/in/username
    - username (will be normalized)

    Args:
        value: LinkedIn URL or path

    Returns:
        Full LinkedIn URL

    Raises:
        PydanticCustomError: If URL format is invalid
    """
    original = value

    # Normalize: add https:// if missing protocol
    if not value.startswith(("http://", "https://")):
        if "/" in value or "." in value:
            # Looks like a URL/path
            value = f"https://{value}"
        else:
            # Assume it's just the username
            value = f"https://linkedin.com/in/{value}"

    # Parse and validate the host
    parsed = urlparse(value)
    host = parsed.hostname or ""

    # Check exact match or subdomain of linkedin.com
    if host != "linkedin.com" and not host.endswith(".linkedin.com"):
        raise PydanticCustomError(
            "linkedin_url",
            "Invalid LinkedIn URL. Expected: linkedin.com/in/username",
            {"value": original},
        )

    # Validate path pattern (allow word chars, hyphens, and periods in usernames)
    if not re.match(r"^/in/[\w\.\-]+/?$", parsed.path):
        raise PydanticCustomError(
            "linkedin_url",
            "Invalid LinkedIn URL. Expected: linkedin.com/in/username",
            {"value": original},
        )

    return value


def validate_github_url(value: str) -> str:
    """Validate and normalize GitHub profile URL.

    Accepts:
    - github.com/username
    - https://github.com/username
    - username (will be normalized)

    Args:
        value: GitHub URL or username

    Returns:
        Full GitHub URL

    Raises:
        PydanticCustomError: If URL format is invalid
    """
    original = value

    # Normalize: add https:// if missing protocol
    if not value.startswith(("http://", "https://")):
        if "/" in value or "." in value:
            # Looks like a URL/path
            value = f"https://{value}"
        else:
            # Assume it's just the username
            value = f"https://github.com/{value}"

    # Parse and validate the host
    parsed = urlparse(value)
    host = parsed.hostname or ""

    # Check exact match or subdomain of github.com
    if host != "github.com" and not host.endswith(".github.com"):
        raise PydanticCustomError(
            "github_url",
            "Invalid GitHub URL. Expected: github.com/username",
            {"value": original},
        )

    # Validate path pattern (username only, not repo paths; allow periods in usernames)
    if not re.match(r"^/[\w\.\-]+/?$", parsed.path):
        raise PydanticCustomError(
            "github_url",
            "Invalid GitHub URL. Expected: github.com/username",
            {"value": original},
        )

    return value


def parse_date_flexible(value: str | date) -> date:
    """Parse date from various string formats.

    Accepts:
    - date objects (pass-through)
    - "YYYY-MM-DD"
    - "MM/YYYY"
    - "YYYY"
    - "Month YYYY" (e.g., "January 2024")

    Args:
        value: Date string or date object

    Returns:
        Parsed date object

    Raises:
        PydanticCustomError: If date format is invalid
    """
    if isinstance(value, date):
        return value

    value_str = value.strip()

    # YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}$", value_str):
        return date.fromisoformat(value_str)

    # MM/YYYY
    if match := re.match(r"^(\d{1,2})/(\d{4})$", value_str):
        month, year = int(match.group(1)), int(match.group(2))
        return date(year, month, 1)

    # YYYY only
    if re.match(r"^\d{4}$", value_str):
        return date(int(value_str), 1, 1)

    # Month YYYY
    months = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }
    if match := re.match(r"^(\w+)\s+(\d{4})$", value_str, re.IGNORECASE):
        month_name = match.group(1).lower()
        year = int(match.group(2))
        if month_name in months:
            return date(year, months[month_name], 1)

    raise PydanticCustomError(
        "date_format",
        "Invalid date format. Expected: YYYY-MM-DD, MM/YYYY, or 'Month YYYY'",
        {"value": value},
    )
