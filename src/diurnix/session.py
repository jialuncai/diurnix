"""Checksummed deterministic session recording and replay."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from diurnix.codec import canonical_dumps, canonical_loads
from diurnix.errors import IntegrityError, ValidationError
from diurnix.integrity import bytes_checksum, content_checksum, verify_content


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


@dataclass(frozen=True, slots=True)
class SessionDifference:
    sequence: int
    left_checksum: str | None
    right_checksum: str | None


def diff_sessions(
    left: tuple[SessionEntry, ...], right: tuple[SessionEntry, ...]
) -> tuple[SessionDifference, ...]:
    differences = []
    for index in range(max(len(left), len(right))):
        left_checksum = left[index].checksum if index < len(left) else None
        right_checksum = right[index].checksum if index < len(right) else None
        if left_checksum != right_checksum:
            differences.append(SessionDifference(index, left_checksum, right_checksum))
    return tuple(differences)


@dataclass(frozen=True, slots=True)
class SessionCheckpoint:
    next_sequence: int
    stream_checksum: str


def checkpoint_session(recorder: SessionRecorder) -> SessionCheckpoint:
    content = recorder.to_jsonl_bytes()
    return SessionCheckpoint(len(recorder.entries), bytes_checksum(content))


def resume_session(content: bytes, checkpoint: SessionCheckpoint) -> SessionRecorder:
    actual_checksum = bytes_checksum(content)
    if actual_checksum != checkpoint.stream_checksum:
        raise IntegrityError(
            "session checkpoint stream checksum mismatch",
            expected=checkpoint.stream_checksum,
            actual=actual_checksum,
        )
    recorder = recorder_from_jsonl_bytes(content)
    if len(recorder.entries) != checkpoint.next_sequence:
        raise IntegrityError(
            "session checkpoint sequence mismatch",
            expected=str(checkpoint.next_sequence),
            actual=str(len(recorder.entries)),
        )
    return recorder


class SessionFileRecorder:
    """Append canonical records without rewriting prior session bytes."""

    def __init__(self, path: Path) -> None:
        self.path = path
        content = path.read_bytes() if path.exists() else b""
        self._recorder = recorder_from_jsonl_bytes(content)

    @property
    def entries(self) -> tuple[SessionEntry, ...]:
        return self._recorder.entries

    def append(self, kind: str, recorded_at: str, payload: dict[str, Any]) -> SessionEntry:
        entry = self._recorder.append(kind, recorded_at, payload)
        line = (canonical_dumps(session_entry_to_dict(entry)) + "\n").encode("utf-8")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("ab") as stream:
            stream.write(line)
            stream.flush()
        return entry


class SessionRecordKind(StrEnum):
    EVENT = "event.input"
    DECISION = "decision.policy"
    RECEIPT = "receipt.tool"
    OBSERVATION = "observation.tool"
    CHECKPOINT = "checkpoint.runtime"


def record_session_item(
    recorder: SessionRecorder,
    kind: SessionRecordKind,
    recorded_at: str,
    payload: dict[str, Any],
) -> SessionEntry:
    return recorder.append(kind.value, recorded_at, payload)


def query_session(
    entries: tuple[SessionEntry, ...],
    *,
    kind_prefix: str | None = None,
    start: int = 0,
    stop: int | None = None,
) -> tuple[SessionEntry, ...]:
    if start < 0 or (stop is not None and stop < start):
        raise ValidationError("invalid session query range")
    upper = len(entries) if stop is None else min(stop, len(entries))
    selected = entries[start:upper]
    if kind_prefix is not None:
        selected = tuple(entry for entry in selected if entry.kind.startswith(kind_prefix))
    return selected


def session_manifest(entries: tuple[SessionEntry, ...], seed: int) -> dict[str, Any]:
    content = SessionRecorder(entries).to_jsonl_bytes()
    return {
        "kind": "session.recording",
        "schema_version": 1,
        "seed": seed,
        "entry_count": len(entries),
        "stream_checksum": bytes_checksum(content),
        "synthetic": True,
    }


def checkpoint_to_dict(checkpoint: SessionCheckpoint) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "next_sequence": checkpoint.next_sequence,
        "stream_checksum": checkpoint.stream_checksum,
    }


def checkpoint_from_dict(value: dict[str, Any]) -> SessionCheckpoint:
    if set(value) != {"schema_version", "next_sequence", "stream_checksum"}:
        raise ValidationError("session checkpoint does not match schema")
    if value.get("schema_version") != 1:
        raise ValidationError("unsupported session checkpoint schema")
    next_sequence = int(value["next_sequence"])
    if next_sequence < 0:
        raise ValidationError("checkpoint sequence cannot be negative")
    return SessionCheckpoint(next_sequence, str(value["stream_checksum"]))


def difference_to_dict(difference: SessionDifference) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "sequence": difference.sequence,
        "left_checksum": difference.left_checksum,
        "right_checksum": difference.right_checksum,
    }


def difference_from_dict(value: dict[str, Any]) -> SessionDifference:
    expected = {"schema_version", "sequence", "left_checksum", "right_checksum"}
    if set(value) != expected or value.get("schema_version") != 1:
        raise ValidationError("session difference does not match schema")
    return SessionDifference(
        int(value["sequence"]),
        None if value["left_checksum"] is None else str(value["left_checksum"]),
        None if value["right_checksum"] is None else str(value["right_checksum"]),
    )


def summarize_session(entries: tuple[SessionEntry, ...]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for entry in entries:
        namespace = entry.kind.split(".", maxsplit=1)[0]
        counts[namespace] = counts.get(namespace, 0) + 1
    return {
        "entry_count": len(entries),
        "kind_counts": dict(sorted(counts.items())),
        "first_recorded_at": entries[0].recorded_at if entries else None,
        "last_recorded_at": entries[-1].recorded_at if entries else None,
    }


def fork_session(entries: tuple[SessionEntry, ...], next_sequence: int) -> SessionRecorder:
    if next_sequence < 0 or next_sequence > len(entries):
        raise ValidationError("session fork boundary is out of range")
    return SessionRecorder(entries[:next_sequence])


def record_loop_state(recorder: SessionRecorder, recorded_at: str, state: Any) -> SessionEntry:
    from diurnix.loop import LoopState

    if not isinstance(state, LoopState):
        raise ValidationError("session loop state has wrong type")
    return recorder.append(
        "checkpoint.loop",
        recorded_at,
        {
            "phase": state.phase.value,
            "step_count": state.step_count,
            "observation_count": len(state.observations),
            "receipt_count": len(state.receipts),
            "stop_reason": state.stop_reason,
        },
    )
