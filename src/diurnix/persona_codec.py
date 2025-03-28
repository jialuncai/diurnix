"""Canonical mapping codec for synthetic personas."""

from __future__ import annotations

from datetime import time
from typing import Any

from diurnix.errors import ValidationError
from diurnix.persona import Correspondent, HabitGoal, MerchantProfile, Persona, WorkHours


def persona_to_dict(persona: Persona) -> dict[str, Any]:
    """Encode all factory inputs into a schema-versioned mapping."""
    return {
        "schema_version": 1,
        "persona_id": persona.persona_id,
        "name": persona.name,
        "timezone": persona.timezone,
        "work_hours": {
            "starts_at": persona.work_hours.starts_at.isoformat(),
            "ends_at": persona.work_hours.ends_at.isoformat(),
            "weekdays": list(persona.work_hours.weekdays),
        },
        "correspondents": [
            {
                "name": item.name,
                "email": item.email,
                "relationship": item.relationship,
                "trusted": item.trusted,
            }
            for item in persona.correspondents
        ],
        "merchants": [
            {
                "name": item.name,
                "category": item.category,
                "typical_amount": item.typical_amount,
                "recurring": item.recurring,
            }
            for item in persona.merchants
        ],
        "habit_goals": [
            {
                "name": item.name,
                "target_days_per_week": item.target_days_per_week,
                "preferred_hour": item.preferred_hour,
                "grace_days": item.grace_days,
            }
            for item in persona.habit_goals
        ],
    }


def persona_from_dict(value: dict[str, Any]) -> Persona:
    """Decode the strict current persona schema."""
    expected = {
        "schema_version",
        "persona_id",
        "name",
        "timezone",
        "work_hours",
        "correspondents",
        "merchants",
        "habit_goals",
    }
    if set(value) != expected or value.get("schema_version") != 1:
        raise ValidationError("persona manifest does not match schema")
    try:
        hours = value["work_hours"]
        return Persona(
            value["persona_id"],
            value["name"],
            value["timezone"],
            WorkHours(
                time.fromisoformat(hours["starts_at"]),
                time.fromisoformat(hours["ends_at"]),
                tuple(hours["weekdays"]),
            ),
            tuple(Correspondent(**item) for item in value["correspondents"]),
            tuple(MerchantProfile(**item) for item in value["merchants"]),
            tuple(HabitGoal(**item) for item in value["habit_goals"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ValidationError("invalid persona manifest payload") from error
