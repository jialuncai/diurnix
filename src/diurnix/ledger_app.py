"""Deterministic household ledger analysis over synthetic transactions."""

from __future__ import annotations

from dataclasses import dataclass

from diurnix.errors import ValidationError
from diurnix.events import AnomalyLabel, Transaction

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


def ewma_deviations(
    transactions: tuple[Transaction, ...], *, alpha: float = 0.3
) -> dict[str, float]:
    if not 0 < alpha <= 1:
        raise ValidationError("EWMA alpha must be between zero and one")
    baselines: dict[str, float] = {}
    result = {}
    for item in sorted(transactions, key=lambda value: (value.occurred_at, value.event_id)):
        amount = abs(item.amount)
        baseline = baselines.get(item.merchant, amount)
        result[item.event_id] = round((amount - baseline) / baseline, 6) if baseline else 0.0
        baselines[item.merchant] = round(alpha * amount + (1 - alpha) * baseline, 6)
    return result


def find_miscategorizations(transactions: tuple[Transaction, ...]) -> tuple[Transaction, ...]:
    return tuple(
        item
        for item in transactions
        if categorize_transaction(item).confidence >= 0.5
        and categorize_transaction(item).category != item.category
    )


def find_subscription_creep(
    transactions: tuple[Transaction, ...], *, minimum_increase: float = 0.05
) -> tuple[Transaction, ...]:
    import itertools

    if minimum_increase <= 0:
        raise ValidationError("subscription increase threshold must be positive")
    grouped: dict[str, list[Transaction]] = {}
    for item in transactions:
        if categorize_transaction(item).category == "subscriptions":
            grouped.setdefault(item.merchant, []).append(item)
    detected = []
    for items in grouped.values():
        ordered = sorted(items, key=lambda item: (item.occurred_at, item.event_id))
        for previous, current in itertools.pairwise(ordered):
            if abs(current.amount) >= abs(previous.amount) * (1 + minimum_increase):
                detected.append(current)
    return tuple(sorted(detected, key=lambda item: (item.occurred_at, item.event_id)))


@dataclass(frozen=True, slots=True)
class AnomalyFinding:
    transaction_id: str
    label: AnomalyLabel
    score: float
    reason: str


def detect_ledger_anomalies(transactions: tuple[Transaction, ...]) -> tuple[AnomalyFinding, ...]:
    findings: dict[str, AnomalyFinding] = {}
    for _, duplicate in find_duplicate_transactions(transactions):
        findings[duplicate.event_id] = AnomalyFinding(
            duplicate.event_id, AnomalyLabel.DUPLICATE, 1.0, "near-time amount and merchant match"
        )
    scores = category_zscores(transactions)
    for item in find_zscore_outliers(transactions, threshold=2.5):
        findings[item.event_id] = AnomalyFinding(
            item.event_id, AnomalyLabel.OUTLIER, scores[item.event_id], "category z-score threshold"
        )
    for item in find_subscription_creep(transactions):
        findings[item.event_id] = AnomalyFinding(
            item.event_id,
            AnomalyLabel.SUBSCRIPTION_CREEP,
            1.0,
            "recurring charge increased above threshold",
        )
    for item in find_miscategorizations(transactions):
        findings[item.event_id] = AnomalyFinding(
            item.event_id,
            AnomalyLabel.MISCATEGORIZED,
            1.0,
            "merchant category differs from stored category",
        )
    return tuple(findings[key] for key in sorted(findings))


def anomaly_metrics(
    transactions: tuple[Transaction, ...], findings: tuple[AnomalyFinding, ...]
) -> dict[str, object]:
    truth = {
        item.event_id: item.planted_anomaly
        for item in transactions
        if item.planted_anomaly is not AnomalyLabel.NONE
    }
    predicted = {item.transaction_id: item.label for item in findings}
    correct = sum(predicted.get(event_id) is label for event_id, label in truth.items())
    precision = round(correct / len(predicted), 6) if predicted else 0.0
    recall = round(correct / len(truth), 6) if truth else 1.0
    slices = {
        label.value: {
            "truth": sum(item is label for item in truth.values()),
            "predicted": sum(item is label for item in predicted.values()),
        }
        for label in AnomalyLabel
        if label is not AnomalyLabel.NONE
    }
    return {
        "transaction_count": len(transactions),
        "truth_count": len(truth),
        "finding_count": len(predicted),
        "precision": precision,
        "recall": recall,
        "slices": slices,
        "synthetic": True,
    }


def monthly_ledger_summary(
    transactions: tuple[Transaction, ...], findings: tuple[AnomalyFinding, ...]
) -> dict[str, object]:
    spending: dict[str, float] = {}
    for item in transactions:
        if item.amount < 0:
            category = categorize_transaction(item).category
            spending[category] = round(spending.get(category, 0.0) + abs(item.amount), 2)
    return {
        "transaction_count": len(transactions),
        "total_spending": round(sum(spending.values()), 2),
        "category_spending": dict(sorted(spending.items())),
        "anomaly_count": len(findings),
        "synthetic": True,
    }


def ledger_svg(summary: dict[str, object], *, width: int = 480, bar_height: int = 24) -> str:
    from html import escape

    if width < 200 or bar_height < 8:
        raise ValidationError("ledger SVG dimensions are too small")
    spending = summary["category_spending"]
    if not isinstance(spending, dict):
        raise ValidationError("ledger category spending must be a mapping")
    maximum = max((float(value) for value in spending.values()), default=1.0)
    height = 40 + len(spending) * (bar_height + 8)
    rows = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" role="img">'
    ]
    rows.append('<rect width="100%" height="100%" fill="white"/>')
    for index, (category, value) in enumerate(sorted(spending.items())):
        y = 24 + index * (bar_height + 8)
        bar_width = round((width - 180) * float(value) / maximum, 2)
        rows.append(f'<text x="8" y="{y + 16}" font-size="12">{escape(str(category))}</text>')
        rows.append(
            f'<rect x="140" y="{y}" width="{bar_width}" height="{bar_height}" fill="#315f8c"/>'
        )
        rows.append(
            f'<text x="{148 + bar_width}" y="{y + 16}" font-size="12">{float(value):.2f}</text>'
        )
    rows.append("</svg>")
    return "".join(rows)


def monthly_ledger_digest(summary: dict[str, object]) -> str:
    lines = [
        "# 家庭账本月报",
        "",
        f"交易数: {summary['transaction_count']}",
        f"支出合计: {float(summary['total_spending']):.2f}",
        f"异常数: {summary['anomaly_count']}",
        "",
        "## 分类支出",
    ]
    spending = summary["category_spending"]
    lines.extend(f"- {category}: {float(value):.2f}" for category, value in spending.items())
    if not spending:
        lines.append("- 无")
    return "\n".join(lines) + "\n"


def ledger_analysis_manifest(
    transactions: tuple[Transaction, ...], findings: tuple[AnomalyFinding, ...], seed: int
) -> dict[str, object]:
    from diurnix.integrity import content_checksum

    summary = monthly_ledger_summary(transactions, findings)
    metrics = anomaly_metrics(transactions, findings)
    return {
        "kind": "ledger.analysis",
        "schema_version": 1,
        "seed": seed,
        "synthetic": True,
        "summary": summary,
        "metrics": metrics,
        "svg_checksum": content_checksum(ledger_svg(summary)),
        "digest_checksum": content_checksum(monthly_ledger_digest(summary)),
    }
