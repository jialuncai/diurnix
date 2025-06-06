from __future__ import annotations

from datetime import UTC, datetime

from diurnix.builtin_tools import default_registry
from diurnix.clock import SyntheticClock
from diurnix.integrity import content_checksum
from diurnix.registry_codec import export_registry, registry_manifest


def test_registry_manifest_covers_all_exported_specs() -> None:
    registry = default_registry(SyntheticClock(datetime(2026, 10, 30, 8, tzinfo=UTC)))
    manifest = registry_manifest(registry)
    assert manifest["kind"] == "tool.registry"
    assert manifest["tool_count"] == 3
    assert manifest["checksum"] == content_checksum(export_registry(registry))


def test_registry_manifest_changes_with_contract() -> None:
    registry = default_registry(SyntheticClock(datetime(2026, 10, 30, 8, tzinfo=UTC)))
    before = registry_manifest(registry)["checksum"]
    registry.unregister("clock.advance")
    assert registry_manifest(registry)["checksum"] != before
