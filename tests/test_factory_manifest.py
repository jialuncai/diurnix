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
