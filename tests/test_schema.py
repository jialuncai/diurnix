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


def test_migration_gaps_reports_every_missing_source_version() -> None:
    from diurnix.schema import migration_gaps

    registry = SchemaRegistry()
    registry.register("event", 2, dict)
    assert migration_gaps(registry, "event", 5) == (1, 3, 4)
    assert migration_gaps(registry, "other", 1) == ()


def test_migration_gaps_rejects_invalid_latest_version() -> None:
    from diurnix.schema import migration_gaps

    with pytest.raises(ValidationError, match="latest"):
        migration_gaps(SchemaRegistry(), "event", 0)
