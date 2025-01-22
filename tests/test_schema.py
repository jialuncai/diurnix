from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.schema import SchemaRegistry


def test_registry_applies_forward_chain_without_mutating_input() -> None:
    registry = SchemaRegistry()
    registry.register("event", 1, lambda value: {**value, "priority": 0})
    registry.register("event", 2, lambda value: {**value, "labels": []})
    original = {"text": "call"}
    assert registry.migrate("event", original, from_version=1, to_version=3) == {
        "text": "call",
        "priority": 0,
        "labels": [],
    }
    assert original == {"text": "call"}
    assert registry.transitions("event") == ((1, 2), (2, 3))


def test_registry_noop_migration_returns_independent_copy() -> None:
    registry = SchemaRegistry()
    original = {"nested": {"count": 1}}
    migrated = registry.migrate("event", original, from_version=2, to_version=2)
    assert migrated == original and migrated is not original
    assert migrated["nested"] is not original["nested"]


def test_registry_rejects_duplicate_transition() -> None:
    registry = SchemaRegistry()
    registry.register("event", 1, dict)
    with pytest.raises(ValidationError, match="already registered"):
        registry.register("event", 1, dict)
