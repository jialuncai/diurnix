from __future__ import annotations

from datetime import UTC, datetime

from diurnix.persona_factory import create_persona
from diurnix.synthetic_ledger import (
    generate_planted_ledger_month,
    ledger_manifest,
)


def test_ledger_manifest_covers_exact_event_bytes_and_truth() -> None:
    transactions = generate_planted_ledger_month(
        create_persona(3), 7, datetime(2026, 10, 1, 8, tzinfo=UTC)
    )
    manifest = ledger_manifest(transactions, seed=7)
    assert manifest == ledger_manifest(transactions, seed=7)
    assert manifest["events"]["count"] == len(transactions)
    assert manifest["ground_truth"]["anomaly_count"] > 0
    assert str(manifest["events"]["checksum"]).startswith("sha256:")
