"""Deterministic NumPy intent routing over synthetic events."""

from __future__ import annotations

import re

_TOKEN = re.compile(r"[A-Za-z0-9]+|[\u4e00-\u9fff]")


def tokenize(text: str) -> tuple[str, ...]:
    return tuple(item.casefold() for item in _TOKEN.findall(text))
