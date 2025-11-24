"""Checksummed deterministic session recording and replay."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from diurnix.codec import canonical_dumps, canonical_loads
from diurnix.errors import IntegrityError, ValidationError
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


class SessionRecorder:
    def __init__(self, entries: tuple[SessionEntry, ...] = ()) -> None:
        if any(entry.sequence != index for index, entry in enumerate(entries)):
            raise ValidationError("session entries must have contiguous sequences")
        self._entries = list(entries)

    @property
    def entries(self) -> tuple[SessionEntry, ...]:
        return tuple(self._entries)

    def append(self, kind: str, recorded_at: str, payload: dict[str, Any]) -> SessionEntry:
        entry = make_session_entry(len(self._entries), kind, recorded_at, payload)
        self._entries.append(entry)
        return entry

    def to_jsonl_bytes(self) -> bytes:
        if not self._entries:
            return b""
        text = "".join(
            canonical_dumps(session_entry_to_dict(entry)) + "\n" for entry in self._entries
        )
        return text.encode("utf-8")


def recorder_from_jsonl_bytes(content: bytes) -> SessionRecorder:
    if not content:
        return SessionRecorder()
    if not content.endswith(b"\n"):
        raise ValidationError("session JSONL must end with newline")
    entries = []
    for line_number, raw in enumerate(content.splitlines(), start=1):
        try:
            value = canonical_loads(raw.decode("utf-8"))
            if not isinstance(value, dict):
                raise ValidationError("session JSONL row must be an object")
            entries.append(session_entry_from_dict(value))
        except (UnicodeDecodeError, ValidationError, IntegrityError) as error:
            raise ValidationError(f"invalid session JSONL line {line_number}: {error}") from error
    return SessionRecorder(tuple(entries))


class SessionReplayer:
    def __init__(self, entries: tuple[SessionEntry, ...]) -> None:
        SessionRecorder(entries)
        self.entries = entries

    def replay(self, reducer: Any, initial: Any) -> Any:
        state = initial
        for entry in self.entries:
            state = reducer(state, entry)
        return state

    def replay_bytes(self) -> bytes:
        return SessionRecorder(self.entries).to_jsonl_bytes()
