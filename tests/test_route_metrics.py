from __future__ import annotations

import pytest

from diurnix.router import Intent, routing_accuracy


def test_routing_accuracy_uses_planted_labels() -> None:
    assert routing_accuracy((Intent.INBOX, Intent.TASKS), (Intent.INBOX, Intent.LEDGER)) == 0.5
    assert routing_accuracy((), ()) == 0.0


def test_routing_accuracy_rejects_length_mismatch() -> None:
    with pytest.raises(ValueError, match="lengths differ"):
        routing_accuracy((Intent.INBOX,), ())
