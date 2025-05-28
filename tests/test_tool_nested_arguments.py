from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.tools import ToolSpec, validate_arguments

SPEC = ToolSpec(
    "mail.send",
    "Send synthetic mail.",
    {
        "type": "object",
        "properties": {
            "recipients": {
                "type": "array",
                "minItems": 1,
                "maxItems": 3,
                "items": {"type": "string", "minLength": 3},
            },
            "metadata": {
                "type": "object",
                "properties": {"urgent": {"type": "boolean"}},
                "required": ["urgent"],
                "additionalProperties": False,
            },
        },
        "required": ["recipients", "metadata"],
    },
    ("mail.send",),
)


def test_nested_arguments_validate_arrays_and_objects() -> None:
    value = {"recipients": ["a@x"], "metadata": {"urgent": False}}
    assert validate_arguments(SPEC, value) == value


def test_nested_array_reports_precise_item_path() -> None:
    with pytest.raises(ValidationError, match="shorter") as captured:
        validate_arguments(SPEC, {"recipients": ["x"], "metadata": {"urgent": False}})
    assert captured.value.context == {"path": "$.arguments.recipients[0]"}


def test_nested_object_reports_required_field_path() -> None:
    with pytest.raises(ValidationError, match="missing required") as captured:
        validate_arguments(SPEC, {"recipients": ["a@x"], "metadata": {}})
    assert captured.value.context == {"path": "$.arguments.metadata"}
