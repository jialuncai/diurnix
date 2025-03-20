from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.persona import MerchantProfile, merchant_categories


def test_merchant_profile_captures_recurring_baseline() -> None:
    profile = MerchantProfile("Synthetic Video", "subscriptions", 18.0, recurring=True)
    assert profile.recurring is True
    assert profile.typical_amount == 18.0


def test_merchant_profile_rejects_blank_and_invalid_amount() -> None:
    with pytest.raises(ValidationError, match="name and category"):
        MerchantProfile("", "food", 10)
    for amount in (0.0, -1.0, float("inf")):
        with pytest.raises(ValidationError, match="positive and finite"):
            MerchantProfile("Market", "food", amount)


def test_merchant_categories_preserve_first_seen_order() -> None:
    items = (
        MerchantProfile("A", "food", 1),
        MerchantProfile("B", "travel", 2),
        MerchantProfile("C", "food", 3),
    )
    assert merchant_categories(items) == ("food", "travel")
