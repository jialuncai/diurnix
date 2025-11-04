from __future__ import annotations

from diurnix.integrity import content_checksum
from diurnix.router import Intent, NumpyRouter, evaluate_router, router_manifest


def test_router_manifest_hashes_executed_synthetic_report() -> None:
    report = evaluate_router(NumpyRouter(), (("budget", Intent.LEDGER),))
    manifest = router_manifest(report, 7)
    assert manifest["synthetic"] is True and manifest["checksum"] == content_checksum(report)
