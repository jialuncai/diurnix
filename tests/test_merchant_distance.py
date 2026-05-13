from __future__ import annotations

from diurnix.ledger_app import merchant_edit_distance


def test_merchant_distance_handles_insert_delete_replace() -> None:
    assert merchant_edit_distance("market", "markets") == 1
    assert merchant_edit_distance("metro", "meto") == 1
    assert merchant_edit_distance("video", "vireo") == 1


def test_merchant_distance_is_symmetric_and_casefolded() -> None:
    assert merchant_edit_distance("Synthetic", "synthetic") == 0
    assert merchant_edit_distance("abc", "ax") == merchant_edit_distance("ax", "abc")
