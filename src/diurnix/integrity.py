"""Checksums for canonical artifacts and byte streams."""

from __future__ import annotations

import hashlib
from typing import Any

from diurnix.codec import canonical_dumps
from diurnix.errors import IntegrityError, ValidationError

CHECKSUM_PREFIX = "sha256:"


def bytes_checksum(content: bytes) -> str:
    """Return an explicitly identified SHA-256 checksum."""
    return CHECKSUM_PREFIX + hashlib.sha256(content).hexdigest()


def content_checksum(value: Any) -> str:
    """Hash the UTF-8 bytes of a canonical JSON representation."""
    return bytes_checksum(canonical_dumps(value).encode("utf-8"))


def validate_checksum(checksum: str) -> None:
    """Validate checksum syntax before doing integrity comparisons."""
    if not checksum.startswith(CHECKSUM_PREFIX):
        raise ValidationError("checksum must use sha256 prefix", path="$.checksum")
    digest = checksum.removeprefix(CHECKSUM_PREFIX)
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ValidationError(
            "checksum must contain 64 lowercase hex characters", path="$.checksum"
        )


def verify_content(value: Any, expected: str) -> None:
    """Raise a structured error if canonical content differs."""
    validate_checksum(expected)
    actual = content_checksum(value)
    if actual != expected:
        raise IntegrityError("content checksum mismatch", expected=expected, actual=actual)
