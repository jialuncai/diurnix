from __future__ import annotations

from diurnix.persona_factory import create_persona
from diurnix.session import SessionRecorder, SessionReplayer


def _run(seed: int) -> bytes:
    persona = create_persona(seed)
    recorder = SessionRecorder()
    recorder.append(
        "event.persona",
        "2026-10-30T09:00:00+08:00",
        {"id": persona.persona_id, "name": persona.name, "timezone": persona.timezone},
    )
    recorder.append("decision.seed", "2026-10-30T09:00:01+08:00", {"seed": seed})
    return SessionReplayer(recorder.entries).replay_bytes()


def test_same_seed_replays_byte_for_byte() -> None:
    for seed in (0, 7, 41):
        assert _run(seed) == _run(seed)


def test_different_seed_changes_recorded_session() -> None:
    assert _run(1) != _run(2)
