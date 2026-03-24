"""Frai shared utilities — slug validation, timestamps, errors."""

from __future__ import annotations

import re
from datetime import datetime, timezone

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
MAX_SLUG = 64


class ServiceError(Exception):
    """Business logic error — shown to user."""

MAX_TITLE = 512
MAX_CONTENT = 100_000


def utcnow_iso() -> str:
    """Return current UTC time as ISO-8601 string (Z suffix for consistency with SQLite triggers)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_slug(slug: str) -> None:
    """Raise ValueError if slug is invalid."""
    if not slug or not SLUG_RE.match(slug):
        raise ValueError(
            f"Invalid slug '{slug}': must match [a-z0-9][a-z0-9-]*"
        )
    if len(slug) > MAX_SLUG:
        raise ValueError(
            f"Slug '{slug[:20]}...' is {len(slug)} chars, max {MAX_SLUG}"
        )


def validate_length(field: str, value: str, limit: int = MAX_TITLE) -> None:
    """Raise ValueError if value exceeds limit."""
    if len(value) > limit:
        raise ValueError(
            f"Field '{field}' is {len(value)} chars, max {limit}"
        )


def validate_content(field: str, value: str | None) -> None:
    """Raise ValueError if content exceeds MAX_CONTENT."""
    if value and len(value) > MAX_CONTENT:
        raise ValueError(
            f"Field '{field}' is {len(value)} chars, max {MAX_CONTENT}"
        )
