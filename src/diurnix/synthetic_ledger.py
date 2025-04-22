"""Seeded household ledger factory with planted anomalies."""

from __future__ import annotations

from datetime import datetime

from diurnix.events import Transaction
from diurnix.persona import Persona
from diurnix.randomness import SeededRandom


def generate_transaction(
    persona: Persona, seed: int, index: int, occurred_at: datetime
) -> Transaction:
    """Generate one ordinary expense near a synthetic merchant baseline."""
    random = SeededRandom(seed).fork(f"ledger-{index}")
    merchant = random.choice(persona.merchants)
    variation = random.integer(-20, 21) / 100
    amount = -round(merchant.typical_amount * (1 + variation), 2)
    return Transaction(
        f"txn_{seed}_{index}", occurred_at, amount, "CNY", merchant.name, merchant.category
    )
