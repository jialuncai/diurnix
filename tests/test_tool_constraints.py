from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.tools import ToolSpec, validate_arguments


def constrained(property_schema: dict[str, object], value: object) -> dict[str, object]:
    spec = ToolSpec(
        "sample",
        "Validate sample.",
        {"type": "object", "properties": {"value": property_schema}, "required": ["value"]},
        ("sample.read",),
    )
    return validate_arguments(spec, {"value": value})


def test_string_length_constraints_include_bounds() -> None:
    schema = {"type": "string", "minLength": 2, "maxLength": 4}
    assert constrained(schema, "ab") == {"value": "ab"}
    assert constrained(schema, "abcd") == {"value": "abcd"}
    with pytest.raises(ValidationError, match="shorter"):
        constrained(schema, "a")
    with pytest.raises(ValidationError, match="longer"):
        constrained(schema, "abcde")


def test_numeric_constraints_include_bounds() -> None:
    schema = {"type": "number", "minimum": 1.5, "maximum": 2.5}
    assert constrained(schema, 1.5) == {"value": 1.5}
    assert constrained(schema, 2.5) == {"value": 2.5}
    with pytest.raises(ValidationError, match="below"):
        constrained(schema, 1.49)
    with pytest.raises(ValidationError, match="above"):
        constrained(schema, 2.51)


def test_enum_constraint_checks_exact_json_value() -> None:
    assert constrained({"type": "string", "enum": ["low", "high"]}, "low") == {"value": "low"}
    with pytest.raises(ValidationError, match="not in enum"):
        constrained({"type": "string", "enum": ["low", "high"]}, "medium")
