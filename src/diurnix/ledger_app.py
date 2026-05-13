"""Deterministic household ledger analysis over synthetic transactions."""

from __future__ import annotations

from dataclasses import dataclass

from diurnix.errors import ValidationError
from diurnix.events import Transaction

_CATEGORY_CUES = {
    "groceries": ("市场", "market", "grocery"),
    "transport": ("地铁", "metro", "taxi", "bus"),
    "subscriptions": ("视频", "video", "subscription"),
    "utilities": ("电力", "water", "utility"),
}


def categorize_merchant(merchant: str) -> tuple[str, tuple[str, ...]]:
    lowered = merchant.casefold()
    for category, cues in _CATEGORY_CUES.items():
        matched = tuple(cue for cue in cues if cue in lowered)
        if matched:
            return category, matched
    return "other", ()


@dataclass(frozen=True, slots=True)
class CategoryResult:
    transaction_id: str
    category: str
    confidence: float
    tells: tuple[str, ...]


def categorize_transaction(transaction: Transaction) -> CategoryResult:
    category, tells = categorize_merchant(transaction.merchant)
    confidence = 0.99 if tells else 0.25
    return CategoryResult(transaction.event_id, category, confidence, tells)


def category_metrics(transactions: tuple[Transaction, ...]) -> dict[str, object]:
    results = tuple(categorize_transaction(item) for item in transactions)
    correct = sum(
        result.category == transaction.category
        for transaction, result in zip(transactions, results, strict=True)
    )
    return {
        "sample_count": len(transactions),
        "accuracy": round(correct / len(transactions), 6) if transactions else 0.0,
        "uncertain_count": sum(result.confidence < 0.5 for result in results),
        "synthetic": True,
    }


@dataclass(frozen=True, slots=True)
class BudgetEnvelope:
    category: str
    allocation: float
    spent: float = 0.0
    rollover: float = 0.0

    def __post_init__(self) -> None:
        if not self.category.strip():
            raise ValidationError("budget category must not be blank")
        if min(self.allocation, self.spent) < 0:
            raise ValidationError("budget allocation and spent values cannot be negative")
        for value in (self.allocation, self.spent, self.rollover):
            if value != value or abs(value) == float("inf"):
                raise ValidationError("budget values must be finite")

    @property
    def available(self) -> float:
        return round(self.allocation + self.rollover - self.spent, 2)


def envelope_to_dict(envelope: BudgetEnvelope) -> dict[str, object]:
    return {
        "schema_version": 1,
        "category": envelope.category,
        "allocation": envelope.allocation,
        "spent": envelope.spent,
        "rollover": envelope.rollover,
        "available": envelope.available,
    }


def envelope_from_dict(value: dict[str, object]) -> BudgetEnvelope:
    expected = {"schema_version", "category", "allocation", "spent", "rollover", "available"}
    if set(value) != expected or value.get("schema_version") != 1:
        raise ValidationError("budget envelope does not match schema")
    envelope = BudgetEnvelope(
        str(value["category"]),
        float(value["allocation"]),
        float(value["spent"]),
        float(value["rollover"]),
    )
    if float(value["available"]) != envelope.available:
        raise ValidationError("budget envelope available value is inconsistent")
    return envelope


def apply_expense(envelope: BudgetEnvelope, transaction: Transaction) -> BudgetEnvelope:
    from dataclasses import replace

    predicted = categorize_transaction(transaction).category
    if predicted != envelope.category:
        raise ValidationError("transaction does not belong to budget envelope")
    if transaction.amount >= 0:
        raise ValidationError("budget expense must have a negative amount")
    return replace(envelope, spent=round(envelope.spent + abs(transaction.amount), 2))


def rollover_envelope(
    envelope: BudgetEnvelope, next_allocation: float, *, carry_overspend: bool = True
) -> BudgetEnvelope:
    carry = envelope.available if carry_overspend else max(0.0, envelope.available)
    return BudgetEnvelope(envelope.category, next_allocation, rollover=round(carry, 2))


def merchant_edit_distance(left: str, right: str) -> int:
    a, b = left.casefold(), right.casefold()
    previous = list(range(len(b) + 1))
    for index, left_char in enumerate(a, start=1):
        current = [index]
        for offset, right_char in enumerate(b, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[offset] + 1,
                    previous[offset - 1] + (left_char != right_char),
                )
            )
        previous = current
    return previous[-1]


def find_duplicate_transactions(
    transactions: tuple[Transaction, ...], *, minutes: int = 10, merchant_distance: int = 1
) -> tuple[tuple[Transaction, Transaction], ...]:
    if minutes < 0 or merchant_distance < 0:
        raise ValidationError("duplicate thresholds cannot be negative")
    ordered = sorted(transactions, key=lambda item: (item.occurred_at, item.event_id))
    pairs = []
    for index, left in enumerate(ordered):
        for right in ordered[index + 1 :]:
            elapsed = (right.occurred_at - left.occurred_at).total_seconds() / 60
            if elapsed > minutes:
                break
            if (
                abs(left.amount - right.amount) <= 0.01
                and left.currency == right.currency
                and merchant_edit_distance(left.merchant, right.merchant) <= merchant_distance
            ):
                pairs.append((left, right))
    return tuple(pairs)


def category_zscores(transactions: tuple[Transaction, ...]) -> dict[str, float]:
    import numpy as np

    by_category: dict[str, list[Transaction]] = {}
    for item in transactions:
        by_category.setdefault(categorize_transaction(item).category, []).append(item)
    scores = {}
    for items in by_category.values():
        values = np.asarray([abs(item.amount) for item in items], dtype=np.float64)
        mean = float(values.mean())
        deviation = float(values.std())
        for item, value in zip(items, values, strict=True):
            scores[item.event_id] = (
                round((float(value) - mean) / deviation, 6) if deviation else 0.0
            )
    return scores


def find_zscore_outliers(
    transactions: tuple[Transaction, ...], *, threshold: float = 3.0
) -> tuple[Transaction, ...]:
    if threshold <= 0:
        raise ValidationError("z-score threshold must be positive")
    scores = category_zscores(transactions)
    return tuple(item for item in transactions if scores.get(item.event_id, 0.0) >= threshold)
