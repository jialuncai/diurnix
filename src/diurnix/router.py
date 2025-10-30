"""Deterministic NumPy intent routing over synthetic events."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

import numpy as np

_TOKEN = re.compile(r"[A-Za-z0-9]+|[\u4e00-\u9fff]")


def tokenize(text: str) -> tuple[str, ...]:
    return tuple(item.casefold() for item in _TOKEN.findall(text))


class Intent(StrEnum):
    INBOX = "inbox"
    CALENDAR = "calendar"
    TASKS = "tasks"
    LEDGER = "ledger"
    HABITS = "habits"


_KEYWORDS = {
    Intent.INBOX: ("mail", "邮件", "回复"),
    Intent.CALENDAR: ("calendar", "日程", "会议"),
    Intent.TASKS: ("task", "任务", "计划"),
    Intent.LEDGER: ("budget", "账单", "消费"),
    Intent.HABITS: ("habit", "习惯", "打卡"),
}


def keyword_counts(text: str) -> dict[Intent, int]:
    lowered = text.casefold()
    return {
        intent: sum(lowered.count(word) for word in words) for intent, words in _KEYWORDS.items()
    }


def recurrence_score(text: str) -> float:
    cues = ("每天", "每周", "daily", "weekly", "routine", "习惯")
    return round(min(1.0, sum(cue in text.casefold() for cue in cues) / 2), 6)


def priority_score(text: str) -> float:
    lowered = text.casefold()
    weights = (("urgent", 1.0), ("紧急", 1.0), ("today", 0.5), ("今天", 0.5), ("!", 0.1))
    return round(min(1.0, sum(weight for cue, weight in weights if cue in lowered)), 6)


@dataclass(frozen=True, slots=True)
class FeatureVector:
    values: tuple[float, ...]
    names: tuple[str, ...]


def extract_features(text: str) -> FeatureVector:
    counts = keyword_counts(text)
    names = (
        *(f"keyword.{intent.value}" for intent in Intent),
        "recurrence",
        "priority",
        "token_count",
    )
    values = (
        *(float(counts[intent]) for intent in Intent),
        recurrence_score(text),
        priority_score(text),
        float(len(tokenize(text))),
    )
    return FeatureVector(values, names)


@dataclass(frozen=True, slots=True)
class RouteResult:
    intent: Intent
    scores: dict[Intent, float]
    ambiguous: bool


class NumpyRouter:
    def __init__(self, ambiguity_band: float = 0.15) -> None:
        if ambiguity_band < 0:
            raise ValueError("ambiguity band cannot be negative")
        self.ambiguity_band = ambiguity_band

    def route(self, text: str) -> RouteResult:
        vector = np.asarray(extract_features(text).values, dtype=np.float64)
        scores = {}
        for index, intent in enumerate(Intent):
            raw = (
                vector[index] * 2
                + (0.8 * vector[5] if intent is Intent.HABITS else 0)
                + (0.2 * vector[6] if intent in (Intent.INBOX, Intent.TASKS) else 0)
            )
            scores[intent] = round(float(raw), 6)
        ordered = sorted(scores, key=lambda item: (-scores[item], item.value))
        gap = scores[ordered[0]] - scores[ordered[1]]
        return RouteResult(ordered[0], scores, gap <= self.ambiguity_band)


def route_probabilities(result: RouteResult) -> dict[Intent, float]:
    values = np.asarray([result.scores[intent] for intent in Intent], dtype=np.float64)
    shifted = values - values.max()
    exp = np.exp(shifted)
    probs = exp / exp.sum()
    rounded = [round(float(item), 6) for item in probs]
    rounded[-1] = round(rounded[-1] + (1 - sum(rounded)), 6)
    return dict(zip(Intent, rounded, strict=True))


def route_requires_approval(result: RouteResult) -> bool:
    return result.ambiguous


def routing_accuracy(predicted: tuple[Intent, ...], truth: tuple[Intent, ...]) -> float:
    if len(predicted) != len(truth):
        raise ValueError("routing lengths differ")
    if not truth:
        return 0.0
    return round(
        sum(left is right for left, right in zip(predicted, truth, strict=True)) / len(truth), 6
    )


def routing_slices(
    predicted: tuple[Intent, ...], truth: tuple[Intent, ...]
) -> dict[str, dict[str, float | int]]:
    if len(predicted) != len(truth):
        raise ValueError("routing lengths differ")
    result = {}
    for intent in Intent:
        indices = [i for i, label in enumerate(truth) if label is intent]
        correct = sum(predicted[i] is intent for i in indices)
        result[intent.value] = {
            "count": len(indices),
            "accuracy": round(correct / len(indices), 6) if indices else 0.0,
        }
    return result


def evaluate_router(
    router: NumpyRouter, items: tuple[tuple[str, Intent], ...]
) -> dict[str, object]:
    predicted = tuple(router.route(text).intent for text, _ in items)
    truth = tuple(label for _, label in items)
    return {
        "sample_count": len(items),
        "accuracy": routing_accuracy(predicted, truth),
        "slices": routing_slices(predicted, truth),
        "ambiguous_count": sum(router.route(text).ambiguous for text, _ in items),
        "synthetic": True,
    }


def route_to_dict(result: RouteResult) -> dict[str, object]:
    return {
        "schema_version": 1,
        "intent": result.intent.value,
        "scores": {intent.value: result.scores[intent] for intent in Intent},
        "ambiguous": result.ambiguous,
    }
