from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.registry import ToolRegistry
from diurnix.tools import ToolSpec


def test_registry_validates_before_invoking_once() -> None:
    calls: list[dict[str, object]] = []
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            "math.double",
            "Double a number.",
            {"type": "object", "properties": {"value": {"type": "number"}}, "required": ["value"]},
            ("math.read",),
        ),
        lambda arguments: calls.append(arguments) or arguments["value"] * 2,
    )
    assert registry.invoke("math.double", {"value": 3}) == 6
    assert calls == [{"value": 3}]
    with pytest.raises(ValidationError, match="expected number"):
        registry.invoke("math.double", {"value": "3"})
    assert calls == [{"value": 3}]


def test_registry_passes_an_independent_argument_mapping() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolSpec("mutate", "Mutate copy.", {"type": "object", "properties": {}}, ("local.write",)),
        lambda arguments: arguments.update({"changed": True}),
    )
    original: dict[str, object] = {}
    registry.invoke("mutate", original)
    assert original == {}
