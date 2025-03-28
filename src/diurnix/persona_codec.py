"""Canonical mapping codec for synthetic personas."""

from __future__ import annotations

from typing import Any

from diurnix.persona import Persona


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
