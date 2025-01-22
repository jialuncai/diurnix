"""Portable identifiers for events, plans, and receipts."""

from __future__ import annotations

import re
from typing import Any

from diurnix.integrity import content_checksum

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")


def validate_identifier(value: str, *, label: str = "identifier") -> str:
    """Return a valid lowercase portable identifier or raise ``ValueError``."""
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"{label} must be a lowercase portable identifier")
    return value


def stable_identifier(namespace: str, value: Any, *, length: int = 16) -> str:
    """Derive a deterministic compact identifier from canonical content."""
    validate_identifier(namespace, label="namespace")
    if not 8 <= length <= 64:
        raise ValueError("identifier digest length must be from 8 to 64")
    digest = content_checksum(value).removeprefix("sha256:")[:length]
    return f"{namespace}_{digest}"
