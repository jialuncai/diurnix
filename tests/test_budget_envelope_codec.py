from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.ledger_app import BudgetEnvelope, envelope_from_dict, envelope_to_dict


def test_budget_envelope_mapping_roundtrips() -> None:
    envelope = BudgetEnvelope("groceries", 500, 120.25, 25.5)
    assert envelope_from_dict(envelope_to_dict(envelope)) == envelope


def test_budget_envelope_codec_rejects_derived_value_drift() -> None:
    encoded = envelope_to_dict(BudgetEnvelope("food", 100, 20))
    encoded["available"] = 999
    with pytest.raises(ValidationError, match="inconsistent"):
        envelope_from_dict(encoded)
