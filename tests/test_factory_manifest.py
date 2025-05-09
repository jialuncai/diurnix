from __future__ import annotations

from datetime import UTC, datetime

from diurnix.factory import bundle_manifest, generate_bundle


def test_bundle_manifest_covers_every_event_stream() -> None:
    bundle = generate_bundle(3, datetime(2026, 10, 1, 8, tzinfo=UTC))
    manifest = bundle_manifest(bundle)
    assert set(manifest["streams"]) == {"inbox", "calendar", "ledger", "habits"}
    for name in manifest["streams"]:
        assert manifest["streams"][name]["count"] == len(getattr(bundle, name))
        assert str(manifest["streams"][name]["checksum"]).startswith("sha256:")
    assert str(manifest["ground_truth_checksum"]).startswith("sha256:")


def test_same_seed_bundle_has_identical_manifests() -> None:
    start = datetime(2026, 10, 1, 8, tzinfo=UTC)
    first = generate_bundle(3, start)
    second = generate_bundle(3, start)
    assert first == second
    assert bundle_manifest(first) == bundle_manifest(second)


def test_different_seed_bundle_changes_all_identity_streams() -> None:
    start = datetime(2026, 10, 1, 8, tzinfo=UTC)
    first = generate_bundle(3, start)
    second = generate_bundle(4, start)
    assert first.persona.persona_id != second.persona.persona_id
    assert {event.event_id for event in first.inbox}.isdisjoint(
        event.event_id for event in second.inbox
    )
    assert bundle_manifest(first) != bundle_manifest(second)
