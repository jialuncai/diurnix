"""Canonical JSON encoding used by every persisted artifact."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any

from diurnix.errors import ValidationError


def normalize(value: Any, *, path: str = "$") -> Any:
    """Normalize supported values without silently stringifying unknown objects."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise ValidationError("non-finite floats are not canonical", path=path)
        return value
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValidationError("datetime must be timezone-aware", path=path)
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Enum):
        return normalize(value.value, path=path)
    if is_dataclass(value) and not isinstance(value, type):
        return normalize(asdict(value), path=path)
    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValidationError("object keys must be strings", path=path)
            normalized[key] = normalize(item, path=f"{path}.{key}")
        return normalized
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [normalize(item, path=f"{path}[{index}]") for index, item in enumerate(value)]
    raise ValidationError(f"unsupported canonical type: {type(value).__name__}", path=path)


def canonical_dumps(value: Any) -> str:
    """Encode a supported value with stable key ordering and compact separators."""
    return json.dumps(normalize(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_loads(text: str) -> Any:
    """Decode JSON while rejecting duplicate object keys and non-standard constants."""

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValidationError("duplicate object key", path=f"$.{key}")
            result[key] = value
        return result

    try:
        return json.loads(
            text,
            object_pairs_hook=pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValidationError(f"invalid constant: {value}")
            ),
        )
    except json.JSONDecodeError as error:
        raise ValidationError(f"invalid JSON at character {error.pos}") from error
