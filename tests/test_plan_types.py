from __future__ import annotations

import pytest

from diurnix.plans import InputRef, ValueType


def test_plan_value_type_wire_contract_is_exhaustive() -> None:
    assert [item.value for item in ValueType] == [
        "string",
        "number",
        "boolean",
        "object",
        "array",
        "any",
    ]


def test_input_reference_preserves_typed_source() -> None:
    assert InputRef("fetch_mail", "messages", ValueType.ARRAY) == InputRef(
        "fetch_mail", "messages", ValueType.ARRAY
    )


def test_input_reference_validates_both_identifiers() -> None:
    with pytest.raises(ValueError, match="step_id"):
        InputRef("Bad Step", "out")
    with pytest.raises(ValueError, match="output"):
        InputRef("step", "Bad Out")
