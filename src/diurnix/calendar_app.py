"""Calendar conflict and rescheduling mechanics for synthetic events."""

from __future__ import annotations

import itertools
from enum import StrEnum

from diurnix.events import CalendarEntry


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
