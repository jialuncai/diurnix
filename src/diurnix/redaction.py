"""Deterministic PII detection and redaction transforms."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

_EMAIL = re.compile(r"(?<![\w.+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.-])")
_PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d -]{8,}\d)(?!\d)")
_CARD = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")


@dataclass(frozen=True, slots=True)
class PiiMatch:
    kind: str
    start: int
    end: int
    text: str


def find_pii(text: str) -> tuple[PiiMatch, ...]:
    """Find non-overlapping email, phone, and card candidates in position order."""
    matches = []
    for kind, pattern in (("email", _EMAIL), ("phone", _PHONE), ("card", _CARD)):
        matches.extend(
            PiiMatch(kind, match.start(), match.end(), match.group())
            for match in pattern.finditer(text)
        )
    ordered = sorted(matches, key=lambda item: (item.start, -(item.end - item.start), item.kind))
    result = []
    for item in ordered:
        if not result or item.start >= result[-1].end:
            result.append(item)
    return tuple(result)


def redact_text(text: str, *, kinds: tuple[str, ...] = ("email", "phone", "card")) -> str:
    """Replace selected PII candidates with stable typed placeholders."""
    accepted = set(kinds)
    pieces = []
    cursor = 0
    for match in find_pii(text):
        if match.kind not in accepted:
            continue
        pieces.append(text[cursor : match.start])
        pieces.append(f"[{match.kind.upper()}]")
        cursor = match.end
    pieces.append(text[cursor:])
    return "".join(pieces)


def redact_value(value: Any) -> Any:
    """Recursively redact string leaves while preserving JSON container shapes."""
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        return {key: redact_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_value(item) for item in value)
    return value


def contains_pii(value: Any) -> bool:
    """Return whether any nested string leaf contains a detected candidate."""
    if isinstance(value, str):
        return bool(find_pii(value))
    if isinstance(value, dict):
        return any(contains_pii(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(contains_pii(item) for item in value)
    return False
