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
