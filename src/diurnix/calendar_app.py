"""Calendar conflict and rescheduling mechanics for synthetic events."""

from __future__ import annotations

import itertools
from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta
from enum import StrEnum

from diurnix.errors import ValidationError
from diurnix.events import CalendarEntry
from diurnix.persona import Persona
from diurnix.persona_factory import work_bounds


class IntervalRelation(StrEnum):
    BEFORE = "before"
    MEETS = "meets"
    OVERLAPS = "overlaps"
    FINISHED_BY = "finished_by"
    CONTAINS = "contains"
    STARTS = "starts"
    EQUALS = "equals"
    STARTED_BY = "started_by"
    DURING = "during"
    FINISHES = "finishes"
    OVERLAPPED_BY = "overlapped_by"
    MET_BY = "met_by"
    AFTER = "after"


def interval_relation(left: CalendarEntry, right: CalendarEntry) -> IntervalRelation:
    a, b, c, d = left.starts_at, left.ends_at, right.starts_at, right.ends_at
    if b < c:
        return IntervalRelation.BEFORE
    if b == c:
        return IntervalRelation.MEETS
    if a < c < b < d:
        return IntervalRelation.OVERLAPS
    if a < c and b == d:
        return IntervalRelation.FINISHED_BY
    if a < c and d < b:
        return IntervalRelation.CONTAINS
    if a == c and b < d:
        return IntervalRelation.STARTS
    if a == c and b == d:
        return IntervalRelation.EQUALS
    if a == c and b > d:
        return IntervalRelation.STARTED_BY
    if c < a and b < d:
        return IntervalRelation.DURING
    if c < a and b == d:
        return IntervalRelation.FINISHES
    if c < a < d < b:
        return IntervalRelation.OVERLAPPED_BY
    if a == d:
        return IntervalRelation.MET_BY
    return IntervalRelation.AFTER


def intervals_conflict(left: CalendarEntry, right: CalendarEntry) -> bool:
    return interval_relation(left, right) not in {
        IntervalRelation.BEFORE,
        IntervalRelation.MEETS,
        IntervalRelation.MET_BY,
        IntervalRelation.AFTER,
    }


def find_calendar_conflicts(
    entries: tuple[CalendarEntry, ...],
) -> tuple[tuple[CalendarEntry, CalendarEntry], ...]:
    ordered = sorted(entries, key=lambda entry: (entry.starts_at, entry.event_id))
    return tuple(
        (left, right)
        for index, left in enumerate(ordered)
        for right in ordered[index + 1 :]
        if intervals_conflict(left, right)
    )


def find_travel_conflicts(
    entries: tuple[CalendarEntry, ...],
) -> tuple[tuple[CalendarEntry, CalendarEntry, int], ...]:
    ordered = sorted(entries, key=lambda entry: (entry.starts_at, entry.event_id))
    conflicts = []
    for left, right in itertools.pairwise(ordered):
        if intervals_conflict(left, right):
            continue
        gap = int((right.starts_at.timestamp() - left.ends_at.timestamp()) // 60)
        required = max(left.travel_minutes, right.travel_minutes)
        if left.location != right.location and gap < required:
            conflicts.append((left, right, required - gap))
    return tuple(conflicts)


@dataclass(frozen=True, slots=True)
class RescheduleProposal:
    entry_id: str
    starts_at: datetime
    ends_at: datetime
    reason: str


def propose_reschedule(
    entry: CalendarEntry,
    entries: tuple[CalendarEntry, ...],
    persona: Persona,
    target_day: date,
    *,
    step_minutes: int = 15,
) -> RescheduleProposal | None:
    if step_minutes < 1:
        raise ValidationError("reschedule step must be positive")
    bounds = work_bounds(persona, target_day)
    if bounds is None:
        return None
    work_start, work_end = bounds
    duration = timedelta(minutes=entry.duration_minutes)
    others = tuple(item for item in entries if item.event_id != entry.event_id)
    candidate_start = work_start
    while candidate_start + duration <= work_end:
        candidate = replace(
            entry,
            occurred_at=candidate_start,
            starts_at=candidate_start,
            ends_at=candidate_start + duration,
            planted_conflict=False,
        )
        proposed = (*others, candidate)
        if not find_calendar_conflicts(proposed) and not find_travel_conflicts(proposed):
            return RescheduleProposal(
                entry.event_id,
                candidate.starts_at,
                candidate.ends_at,
                "first available slot within work hours",
            )
        candidate_start += timedelta(minutes=step_minutes)
    return None


def proposal_to_dict(proposal: RescheduleProposal) -> dict[str, object]:
    return {
        "schema_version": 1,
        "entry_id": proposal.entry_id,
        "starts_at": proposal.starts_at.isoformat(),
        "ends_at": proposal.ends_at.isoformat(),
        "reason": proposal.reason,
    }


def proposal_from_dict(value: dict[str, object]) -> RescheduleProposal:
    from datetime import datetime

    expected = {"schema_version", "entry_id", "starts_at", "ends_at", "reason"}
    if set(value) != expected or value.get("schema_version") != 1:
        raise ValidationError("calendar proposal does not match schema")
    try:
        starts_at = datetime.fromisoformat(str(value["starts_at"]))
        ends_at = datetime.fromisoformat(str(value["ends_at"]))
    except ValueError as error:
        raise ValidationError("calendar proposal has invalid time") from error
    if starts_at.tzinfo is None or ends_at.tzinfo is None or ends_at <= starts_at:
        raise ValidationError("calendar proposal bounds are invalid")
    return RescheduleProposal(str(value["entry_id"]), starts_at, ends_at, str(value["reason"]))


def calendar_digest(entries: tuple[CalendarEntry, ...]) -> str:
    overlap = find_calendar_conflicts(entries)
    travel = find_travel_conflicts(entries)
    lines = [
        "# 日程检查",
        "",
        f"日程数: {len(entries)}",
        f"重叠冲突: {len(overlap)}",
        f"行程缓冲冲突: {len(travel)}",
        "",
        "## 重叠明细",
    ]
    lines.extend(
        f"- {left.event_id} ↔ {right.event_id}: {interval_relation(left, right).value}"
        for left, right in overlap
    )
    if not overlap:
        lines.append("- 无")
    return "\n".join(lines) + "\n"


def calendar_conflict_metrics(entries: tuple[CalendarEntry, ...]) -> dict[str, object]:
    truth = {entry.event_id for entry in entries if entry.planted_conflict}
    pairs = find_calendar_conflicts(entries)
    predicted = {entry.event_id for pair in pairs for entry in pair}
    true_positive = len(truth & predicted)
    precision = round(true_positive / len(predicted), 6) if predicted else 0.0
    recall = round(true_positive / len(truth), 6) if truth else 1.0
    return {
        "entry_count": len(entries),
        "planted_conflict_count": len(truth),
        "predicted_conflict_count": len(predicted),
        "precision": precision,
        "recall": recall,
        "synthetic": True,
    }


def propose_conflict_resolutions(
    entries: tuple[CalendarEntry, ...], persona: Persona
) -> tuple[RescheduleProposal, ...]:
    proposals = []
    for entry in sorted(entries, key=lambda item: (item.starts_at, item.event_id)):
        if not entry.planted_conflict:
            continue
        proposal = propose_reschedule(entry, entries, persona, entry.starts_at.date())
        if proposal is not None:
            proposals.append(proposal)
    return tuple(proposals)
