"""Seeded household ledger factory with planted anomalies."""

from __future__ import annotations

from datetime import datetime, timedelta

from diurnix.events import AnomalyLabel, Transaction
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


def plant_duplicate(source: Transaction, seed: int) -> Transaction:
    """Create a near-time duplicate retaining amount and merchant."""
    return Transaction(
        f"txn_duplicate_{seed}",
        source.occurred_at + timedelta(minutes=3),
        source.amount,
        source.currency,
        source.merchant,
        source.category,
        AnomalyLabel.DUPLICATE,
    )


def plant_outlier(source: Transaction, seed: int, *, multiplier: float = 8.0) -> Transaction:
    """Create a labeled expense multiple while preserving merchant context."""
    if multiplier <= 1:
        from diurnix.errors import ValidationError

        raise ValidationError("outlier multiplier must exceed one")
    return Transaction(
        f"txn_outlier_{seed}",
        source.occurred_at,
        round(source.amount * multiplier, 2),
        source.currency,
        source.merchant,
        source.category,
        AnomalyLabel.OUTLIER,
    )


def plant_subscription_creep(
    persona: Persona, seed: int, start: datetime, *, months: int = 4
) -> tuple[Transaction, ...]:
    """Generate a recurring subscription whose charge rises each month."""
    merchant = next((item for item in persona.merchants if item.recurring), None)
    if merchant is None:
        from diurnix.errors import ValidationError

        raise ValidationError("persona has no recurring merchant")
    return tuple(
        Transaction(
            f"txn_creep_{seed}_{month}",
            start + timedelta(days=30 * month),
            -round(merchant.typical_amount * (1 + 0.08 * month), 2),
            "CNY",
            merchant.name,
            merchant.category,
            AnomalyLabel.SUBSCRIPTION_CREEP if month else AnomalyLabel.NONE,
        )
        for month in range(months)
    )


def plant_miscategorization(source: Transaction, seed: int) -> Transaction:
    """Copy a transaction with a known-wrong category."""
    wrong = "transport" if source.category != "transport" else "groceries"
    return Transaction(
        f"txn_miscategorized_{seed}",
        source.occurred_at,
        source.amount,
        source.currency,
        source.merchant,
        wrong,
        AnomalyLabel.MISCATEGORIZED,
    )


def generate_planted_ledger_month(
    persona: Persona, seed: int, start: datetime
) -> tuple[Transaction, ...]:
    """Generate a month containing every documented planted anomaly family."""
    base = list(generate_ledger_month(persona, seed, start))
    base.extend(
        (
            plant_duplicate(base[3], seed),
            plant_outlier(base[10], seed),
            plant_miscategorization(base[20], seed),
        )
    )
    base.extend(plant_subscription_creep(persona, seed, start))
    return tuple(sorted(base, key=lambda item: (item.occurred_at, item.event_id)))


def ledger_ground_truth(transactions: tuple[Transaction, ...]) -> dict[str, object]:
    """Return labeled anomaly IDs and class counts."""
    anomaly_ids = {
        item.event_id: item.planted_anomaly.value
        for item in transactions
        if item.planted_anomaly is not AnomalyLabel.NONE
    }
    return {
        "transaction_count": len(transactions),
        "anomaly_ids": anomaly_ids,
        "anomaly_count": len(anomaly_ids),
    }
