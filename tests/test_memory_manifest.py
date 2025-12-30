from __future__ import annotations

from diurnix.integrity import content_checksum
from diurnix.memory import MemoryStore, memory_manifest, memory_snapshot


def test_memory_manifest_marks_synthetic_empty_store() -> None:
    store = MemoryStore()
    manifest = memory_manifest(store, seed=9)
    assert manifest["synthetic"] is True
    assert manifest["scope_counts"] == {"working": 0, "session": 0, "persistent": 0}
    assert manifest["snapshot_checksum"] == content_checksum(memory_snapshot(store))
