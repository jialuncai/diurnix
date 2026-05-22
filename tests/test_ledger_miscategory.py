from __future__ import annotations

from datetime import UTC, datetime

from diurnix.ledger_app import find_miscategorizations
from diurnix.persona_factory import create_persona
from diurnix.synthetic_ledger import generate_planted_ledger_month


def test_miscategory_detector_recovers_planted_charge() -> None:
    transactions = generate_planted_ledger_month(
        create_persona(6), 6, datetime(2026, 1, 1, tzinfo=UTC)
    )
    detected = {item.event_id for item in find_miscategorizations(transactions)}
    assert detected == {"txn_miscategorized_6"}


def test_miscategory_detector_does_not_guess_unknown_merchants() -> None:
    from diurnix.events import Transaction

    item = Transaction("unknown", datetime(2026, 1, 1, tzinfo=UTC), -5, "CNY", "Elsewhere", "other")
    assert find_miscategorizations((item,)) == ()


def test_miscategory_detection_uses_merchant_not_planted_label() -> None:
    from diurnix.events import AnomalyLabel, Transaction

    item = Transaction(
        "labeled",
        datetime(2026, 1, 1, tzinfo=UTC),
        -5,
        "CNY",
        "合成市场",
        "groceries",
        AnomalyLabel.MISCATEGORIZED,
    )
    assert find_miscategorizations((item,)) == ()


def test_wrong_stored_category_is_detected_without_truth_label() -> None:
    from diurnix.events import Transaction

    item = Transaction(
        "wrong", datetime(2026, 1, 1, tzinfo=UTC), -5, "CNY", "合成地铁", "groceries"
    )
    assert find_miscategorizations((item,)) == (item,)
