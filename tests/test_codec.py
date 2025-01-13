from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime

import pytest

from diurnix.codec import canonical_dumps, canonical_loads
from diurnix.errors import ValidationError


@dataclass(frozen=True)
class Sample:
    when: datetime
    label: str


def test_canonical_json_sorts_nested_keys_and_preserves_unicode() -> None:
    value = {"z": [3, {"b": 2, "a": "早"}], "a": True}
    assert canonical_dumps(value) == '{"a":true,"z":[3,{"a":"早","b":2}]}'


def test_canonical_json_normalizes_temporal_dataclass_values() -> None:
    sample = Sample(datetime(2026, 1, 2, 3, 4, tzinfo=UTC), "wake")
    assert canonical_loads(canonical_dumps(sample)) == {
        "label": "wake",
        "when": "2026-01-02T03:04:00+00:00",
    }
    assert canonical_dumps(date(2026, 1, 2)) == '"2026-01-02"'


def test_canonical_json_rejects_naive_datetime() -> None:
    with pytest.raises(ValidationError, match="timezone-aware") as captured:
        canonical_dumps({"when": datetime(2026, 1, 2)})
    assert captured.value.context == {"path": "$.when"}
