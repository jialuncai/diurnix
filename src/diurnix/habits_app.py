"""Timezone-safe habit streaks and routine scheduling."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from diurnix.errors import ValidationError
from diurnix.events import HabitCheckIn, HabitStatus


def group_habit_checkins(events: tuple[HabitCheckIn, ...]) -> dict[str, tuple[HabitCheckIn, ...]]:
    grouped: dict[str, list[HabitCheckIn]] = {}
    for event in events:
        grouped.setdefault(event.habit, []).append(event)
    result = {}
    for habit, items in sorted(grouped.items()):
        ordered = tuple(sorted(items, key=lambda item: (item.local_date, item.event_id)))
        if len({item.local_date for item in ordered}) != len(ordered):
            raise ValidationError(f"duplicate local habit date: {habit}")
        result[habit] = ordered
    return result


@dataclass(frozen=True, slots=True)
class StreakSummary:
    habit: str
    current: int
    longest: int
    done_days: int
    grace_days_used: int


def calculate_streak(events: tuple[HabitCheckIn, ...], *, grace_days: int = 0) -> StreakSummary:
    if grace_days < 0:
        raise ValidationError("streak grace days cannot be negative")
    if not events:
        return StreakSummary("", 0, 0, 0, 0)
    grouped = group_habit_checkins(events)
    if len(grouped) != 1:
        raise ValidationError("streak calculation requires one habit")
    habit, ordered = next(iter(grouped.items()))
    current = longest = done_days = grace_used = grace_in_streak = 0
    previous_day = None
    for event in ordered:
        day = date.fromisoformat(event.local_date)
        if previous_day is not None and (day - previous_day).days != 1:
            current = 0
            grace_in_streak = 0
        if event.status is HabitStatus.DONE:
            current += 1
            done_days += 1
        elif event.status is HabitStatus.SKIPPED and grace_in_streak < grace_days:
            current += 1
            grace_in_streak += 1
            grace_used += 1
        else:
            current = 0
            grace_in_streak = 0
        longest = max(longest, current)
        previous_day = day
    return StreakSummary(habit, current, longest, done_days, grace_used)


def streak_for_goal(events: tuple[HabitCheckIn, ...], goal: object) -> StreakSummary:
    from diurnix.persona import HabitGoal

    if not isinstance(goal, HabitGoal):
        raise ValidationError("streak goal has wrong type")
    selected = tuple(event for event in events if event.habit == goal.name)
    return calculate_streak(selected, grace_days=goal.grace_days)


def habit_consistency(events: tuple[HabitCheckIn, ...], target_days_per_week: int) -> float:
    if not 1 <= target_days_per_week <= 7:
        raise ValidationError("habit target must be from one to seven")
    if not events:
        return 0.0
    ordered = next(iter(group_habit_checkins(events).values()))
    span_days = (
        date.fromisoformat(ordered[-1].local_date) - date.fromisoformat(ordered[0].local_date)
    ).days + 1
    expected = target_days_per_week * span_days / 7
    done = sum(event.status is HabitStatus.DONE for event in ordered)
    return round(min(1.0, done / expected), 6) if expected else 0.0


@dataclass(frozen=True, slots=True)
class LapseSpan:
    habit: str
    starts_on: str
    ends_on: str
    event_ids: tuple[str, ...]


def detect_lapse_spans(
    events: tuple[HabitCheckIn, ...], *, minimum_days: int = 2
) -> tuple[LapseSpan, ...]:
    if minimum_days < 1:
        raise ValidationError("lapse minimum days must be positive")
    spans = []
    for habit, ordered in group_habit_checkins(events).items():
        run: list[HabitCheckIn] = []
        for event in (*ordered, None):
            consecutive = (
                event is not None
                and event.status is HabitStatus.MISSED
                and (
                    not run
                    or (
                        date.fromisoformat(event.local_date)
                        - date.fromisoformat(run[-1].local_date)
                    ).days
                    == 1
                )
            )
            if consecutive:
                run.append(event)
                continue
            if len(run) >= minimum_days:
                spans.append(
                    LapseSpan(
                        habit,
                        run[0].local_date,
                        run[-1].local_date,
                        tuple(item.event_id for item in run),
                    )
                )
            run = [event] if event is not None and event.status is HabitStatus.MISSED else []
    return tuple(spans)


def lapse_recovery_metrics(
    events: tuple[HabitCheckIn, ...], spans: tuple[LapseSpan, ...]
) -> dict[str, object]:
    truth = {event.event_id for event in events if event.planted_lapse}
    predicted = {event_id for span in spans for event_id in span.event_ids}
    true_positive = len(truth & predicted)
    return {
        "planted_count": len(truth),
        "predicted_count": len(predicted),
        "precision": round(true_positive / len(predicted), 6) if predicted else 0.0,
        "recall": round(true_positive / len(truth), 6) if truth else 1.0,
        "synthetic": True,
    }


@dataclass(frozen=True, slots=True)
class HabitLoop:
    habit: str
    cue: str
    routine: str
    reward: str

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.habit, self.cue, self.routine, self.reward)):
            raise ValidationError("habit loop fields must not be blank")
