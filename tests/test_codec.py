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


def test_canonical_json_rejects_duplicate_keys() -> None:
    with pytest.raises(ValidationError, match="duplicate") as captured:
        canonical_loads('{"same":1,"same":2}')
    assert captured.value.context == {"path": "$.same"}


def test_canonical_json_rejects_nonfinite_numbers_in_both_directions() -> None:
    with pytest.raises(ValidationError, match="non-finite"):
        canonical_dumps({"score": float("nan")})
    with pytest.raises(ValidationError, match="invalid constant"):
        canonical_loads('{"score":NaN}')


def test_canonical_json_rejects_unsupported_values_without_coercion() -> None:
    with pytest.raises(ValidationError, match="unsupported canonical type") as captured:
        canonical_dumps({"payload": object()})
    assert captured.value.context == {"path": "$.payload"}


def test_canonical_json_rejects_nonstring_mapping_keys() -> None:
    with pytest.raises(ValidationError, match="keys must be strings"):
        canonical_dumps({1: "one"})
