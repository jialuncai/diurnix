"""Timezone-safe habit streaks and routine scheduling."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

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
            if consecutive and event is not None:
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


def habit_loop_to_dict(loop: HabitLoop) -> dict[str, object]:
    return {
        "schema_version": 1,
        "habit": loop.habit,
        "cue": loop.cue,
        "routine": loop.routine,
        "reward": loop.reward,
    }


def habit_loop_from_dict(value: dict[str, object]) -> HabitLoop:
    expected = {"schema_version", "habit", "cue", "routine", "reward"}
    if set(value) != expected or value.get("schema_version") != 1:
        raise ValidationError("habit loop does not match schema")
    return HabitLoop(
        str(value["habit"]), str(value["cue"]), str(value["routine"]), str(value["reward"])
    )


@dataclass(frozen=True, slots=True)
class RoutineSchedule:
    habit: str
    starts_at: datetime
    ends_at: datetime


def schedule_routine(
    goal: object,
    day: date,
    calendar: tuple[object, ...],
    timezone_name: str,
    *,
    duration_minutes: int = 20,
    search_minutes: int = 180,
) -> RoutineSchedule | None:
    from diurnix.calendar import local_datetime
    from diurnix.calendar_app import intervals_conflict
    from diurnix.events import CalendarEntry
    from diurnix.persona import HabitGoal

    if not isinstance(goal, HabitGoal):
        raise ValidationError("routine goal has wrong type")
    if duration_minutes < 1 or search_minutes < 0:
        raise ValidationError("routine schedule bounds are invalid")
    preferred = local_datetime(day, time(goal.preferred_hour), timezone_name)
    for offset in range(0, search_minutes + 1, 15):
        starts_at = preferred + timedelta(minutes=offset)
        ends_at = starts_at + timedelta(minutes=duration_minutes)
        candidate = CalendarEntry(
            "routine_candidate", starts_at, goal.name, starts_at, ends_at, "routine"
        )
        if not any(
            isinstance(entry, CalendarEntry) and intervals_conflict(candidate, entry)
            for entry in calendar
        ):
            return RoutineSchedule(goal.name, starts_at, ends_at)
    return None


def routine_schedule_to_dict(schedule: RoutineSchedule) -> dict[str, object]:
    return {
        "schema_version": 1,
        "habit": schedule.habit,
        "starts_at": schedule.starts_at.isoformat(),
        "ends_at": schedule.ends_at.isoformat(),
    }


def routine_schedule_from_dict(value: dict[str, object]) -> RoutineSchedule:
    expected = {"schema_version", "habit", "starts_at", "ends_at"}
    if set(value) != expected or value.get("schema_version") != 1:
        raise ValidationError("routine schedule does not match schema")
    try:
        starts_at = datetime.fromisoformat(str(value["starts_at"]))
        ends_at = datetime.fromisoformat(str(value["ends_at"]))
    except ValueError as error:
        raise ValidationError("routine schedule time is invalid") from error
    if starts_at.tzinfo is None or ends_at.tzinfo is None or ends_at <= starts_at:
        raise ValidationError("routine schedule bounds are invalid")
    return RoutineSchedule(str(value["habit"]), starts_at, ends_at)


def habit_nudge(summary: StreakSummary, schedule: RoutineSchedule | None) -> str:
    from html import escape

    habit = escape(summary.habit, quote=True)
    if schedule is None:
        return f"{habit}: 今天没有可用时段\N{FULLWIDTH COMMA}请手动选择一个短时段。"
    local_time = schedule.starts_at.strftime("%H:%M")
    if summary.current == 0:
        return f"{habit}: {local_time} 从一个小步骤重新开始。"
    return f"{habit}: {local_time} 继续当前 {summary.current} 天连续记录。"


def habit_heatmap_svg(events: tuple[HabitCheckIn, ...], *, cell_size: int = 14) -> str:
    from html import escape

    if cell_size < 8:
        raise ValidationError("habit heatmap cell size is too small")
    grouped = group_habit_checkins(events)
    dates = sorted({event.local_date for event in events})
    width = 130 + max(1, len(dates)) * cell_size
    height = 30 + max(1, len(grouped)) * (cell_size + 6)
    colors = {
        HabitStatus.DONE: "#2f855a",
        HabitStatus.SKIPPED: "#d69e2e",
        HabitStatus.MISSED: "#c53030",
    }
    rows = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" role="img">'
    ]
    rows.append('<rect width="100%" height="100%" fill="white"/>')
    for row, (habit, items) in enumerate(grouped.items()):
        y = 20 + row * (cell_size + 6)
        rows.append(f'<text x="4" y="{y + 11}" font-size="11">{escape(habit)}</text>')
        by_date = {item.local_date: item for item in items}
        for column, local_day in enumerate(dates):
            item = by_date.get(local_day)
            color = colors[item.status] if item else "#e2e8f0"
            x = 120 + column * cell_size
            rows.append(
                f'<rect x="{x}" y="{y}" width="{cell_size - 2}"'
                f' height="{cell_size - 2}" fill="{color}">'
                f"<title>{escape(habit)} {local_day}</title></rect>"
            )
    rows.append("</svg>")
    return "".join(rows)


def habit_consistency_report(
    events: tuple[HabitCheckIn, ...], goals: tuple[object, ...]
) -> dict[str, object]:
    from diurnix.persona import HabitGoal

    rows = []
    for goal in goals:
        if not isinstance(goal, HabitGoal):
            raise ValidationError("habit report goal has wrong type")
        selected = tuple(event for event in events if event.habit == goal.name)
        streak = calculate_streak(selected, grace_days=goal.grace_days)
        rows.append(
            {
                "habit": goal.name,
                "checkin_count": len(selected),
                "consistency": habit_consistency(selected, goal.target_days_per_week),
                "current_streak": streak.current,
                "longest_streak": streak.longest,
                "grace_days_used": streak.grace_days_used,
            }
        )
    return {"habit_count": len(rows), "habits": rows, "synthetic": True}


def habit_consistency_digest(report: dict[str, object], lapse_metrics: dict[str, object]) -> str:
    recall = lapse_metrics["recall"]
    habits = report["habits"]
    if not isinstance(recall, (int, float)) or not isinstance(habits, list):
        raise ValidationError("habit report fields have invalid types")
    lines = [
        "# 习惯一致性报告",
        "",
        f"习惯数: {report['habit_count']}",
        f"种植断档召回率: {float(recall):.2%}",
        "",
        "## 各习惯",
    ]
    for row in habits:
        if not isinstance(row, dict):
            raise ValidationError("habit report rows must be mappings")
        lines.append(
            f"- {row['habit']}: 一致性 {float(row['consistency']):.2%}, "
            f"当前连续 {row['current_streak']} 天"
        )
    if not habits:
        lines.append("- 无")
    return "\n".join(lines) + "\n"


def habit_analysis_manifest(
    events: tuple[HabitCheckIn, ...], report: dict[str, object], seed: int
) -> dict[str, object]:
    from diurnix.integrity import content_checksum

    spans = detect_lapse_spans(events)
    metrics = lapse_recovery_metrics(events, spans)
    return {
        "kind": "habits.analysis",
        "schema_version": 1,
        "seed": seed,
        "synthetic": True,
        "metrics": metrics,
        "report_checksum": content_checksum(report),
        "heatmap_checksum": content_checksum(habit_heatmap_svg(events)),
    }
