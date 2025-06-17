"""Deterministic PII detection and redaction transforms."""

from __future__ import annotations

import re
from dataclasses import dataclass

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
