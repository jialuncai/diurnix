from __future__ import annotations

from diurnix.registry import ToolRegistry
from diurnix.registry_codec import export_registry
from diurnix.tools import SideEffect, ToolSpec


def sample_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            "mail.send",
            "Send synthetic mail.",
            {"type": "object", "properties": {"text": {"type": "string"}}},
            ("mail.send",),
            SideEffect.EXTERNAL,
            2,
        ),
        lambda arguments: arguments,
    )
    return registry


def test_registry_export_contains_specs_but_not_callables() -> None:
    exported = export_registry(sample_registry())
    assert exported == {
        "schema_version": 1,
        "tools": [
            {
                "name": "mail.send",
                "description": "Send synthetic mail.",
                "arguments": {"type": "object", "properties": {"text": {"type": "string"}}},
                "capabilities": ["mail.send"],
                "side_effect": "external",
                "version": 2,
            }
        ],
    }


def test_registry_export_roundtrips_with_explicit_binding() -> None:
    from diurnix.registry_codec import import_registry

    exported = export_registry(sample_registry())
    restored = import_registry(exported, {"mail.send": lambda arguments: arguments})
    assert export_registry(restored) == exported


def test_registry_import_requires_schema_and_binding() -> None:
    import pytest

    from diurnix.errors import ValidationError
    from diurnix.registry_codec import import_registry

    exported = export_registry(sample_registry())
    with pytest.raises(ValidationError, match="missing tool binding"):
        import_registry(exported, {})
    with pytest.raises(ValidationError, match="match schema"):
        import_registry({**exported, "schema_version": 2}, {})


def test_registry_export_has_stable_canonical_json() -> None:
    from diurnix.codec import canonical_dumps

    assert canonical_dumps(export_registry(sample_registry())) == (
        '{"schema_version":1,"tools":[{"arguments":{"properties":{"text":{"type":"string"}},'
        '"type":"object"},"capabilities":["mail.send"],"description":"Send synthetic mail.",'
        '"name":"mail.send","side_effect":"external","version":2}]}'
    )


def test_registry_export_order_is_name_stable() -> None:
    from diurnix.tools import ToolSpec

    registry = sample_registry()
    registry.register(
        ToolSpec("alpha", "Alpha tool.", {"type": "object", "properties": {}}, ("alpha.read",)),
        lambda arguments: None,
    )
    assert [item["name"] for item in export_registry(registry)["tools"]] == ["alpha", "mail.send"]
