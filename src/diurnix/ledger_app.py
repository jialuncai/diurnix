"""Deterministic household ledger analysis over synthetic transactions."""

from __future__ import annotations

from dataclasses import dataclass

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
