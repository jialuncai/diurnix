from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.tools import ToolSpec, validate_arguments

SPEC = ToolSpec(
    "task.create",
    "Create one local task.",
    {
        "type": "object",
        "properties": {"title": {"type": "string"}, "priority": {"type": "integer"}},
        "required": ["title"],
        "additionalProperties": False,
    },
    ("task.write",),
)


def test_argument_validator_accepts_required_and_optional_fields() -> None:
    arguments = {"title": "Review", "priority": 2}
    result = validate_arguments(SPEC, arguments)
    assert result == arguments and result is not arguments


def test_argument_validator_reports_missing_and_unknown_fields() -> None:
    with pytest.raises(ValidationError, match="missing required arguments: title"):
        validate_arguments(SPEC, {})
    with pytest.raises(ValidationError, match="unknown arguments: extra"):
        validate_arguments(SPEC, {"title": "Review", "extra": True})


def test_argument_validator_distinguishes_booleans_from_numbers() -> None:
    with pytest.raises(ValidationError, match="expected integer") as captured:
        validate_arguments(SPEC, {"title": "Review", "priority": True})
    assert captured.value.context == {"path": "$.arguments.priority"}


def test_argument_validator_rejects_unknown_schema_type_at_value_path() -> None:
    invalid = ToolSpec(
        "bad",
        "Bad schema.",
        {"type": "object", "properties": {"value": {"type": "date"}}},
        ("bad.read",),
    )
    with pytest.raises(ValidationError, match="unsupported schema type") as captured:
        validate_arguments(invalid, {"value": "2026-10-30"})
    assert captured.value.context == {"path": "$.arguments.value"}


def test_argument_validator_allows_explicit_additional_properties() -> None:
    open_spec = ToolSpec(
        "open",
        "Open arguments.",
        {"type": "object", "properties": {}, "additionalProperties": True},
        ("open.read",),
    )
    assert validate_arguments(open_spec, {"extra": {"any": "json"}}) == {"extra": {"any": "json"}}
