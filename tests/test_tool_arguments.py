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
