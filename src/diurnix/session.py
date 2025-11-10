"""Checksummed deterministic session recording and replay."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from diurnix.errors import ValidationError
from diurnix.integrity import content_checksum, verify_content


@dataclass(frozen=True, slots=True)
class SessionEntry:
    sequence: int
    kind: str
    recorded_at: str
    payload: dict[str, Any]
    checksum: str


def make_session_entry(
    sequence: int, kind: str, recorded_at: str, payload: dict[str, Any]
) -> SessionEntry:
    if sequence < 0:
        raise ValidationError("session sequence cannot be negative", path="$.sequence")
    if not kind or "." not in kind:
        raise ValidationError("session kind must be a dotted name", path="$.kind")
    body = {"sequence": sequence, "kind": kind, "recorded_at": recorded_at, "payload": payload}
    return SessionEntry(sequence, kind, recorded_at, dict(payload), content_checksum(body))


def session_entry_to_dict(entry: SessionEntry) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "sequence": entry.sequence,
        "kind": entry.kind,
        "recorded_at": entry.recorded_at,
        "payload": entry.payload,
        "checksum": entry.checksum,
    }


def session_entry_from_dict(value: dict[str, Any]) -> SessionEntry:
    expected = {"schema_version", "sequence", "kind", "recorded_at", "payload", "checksum"}
    if set(value) != expected or value.get("schema_version") != 1:
        raise ValidationError("session entry does not match schema")
    entry = make_session_entry(
        int(value["sequence"]), str(value["kind"]), str(value["recorded_at"]), value["payload"]
    )
    verify_content(
        {
            "sequence": entry.sequence,
            "kind": entry.kind,
            "recorded_at": entry.recorded_at,
            "payload": entry.payload,
        },
        str(value["checksum"]),
    )
    return entry
