"""Seeded household ledger factory with planted anomalies."""

from __future__ import annotations

from datetime import datetime, timedelta

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


def generate_ledger_month(
    persona: Persona, seed: int, start: datetime, *, days: int = 30
) -> tuple[Transaction, ...]:
    """Generate two ordinary expenses per synthetic day."""
    from diurnix.errors import ValidationError

    if not 1 <= days <= 31:
        raise ValidationError("ledger days must be from one to 31")
    return tuple(
        generate_transaction(
            persona, seed, day * 2 + slot, start + timedelta(days=day, hours=slot * 6)
        )
        for day in range(days)
        for slot in range(2)
    )
