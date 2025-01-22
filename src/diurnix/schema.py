"""Explicit schema migration registry for persisted mappings."""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Any

from diurnix.errors import ValidationError

Migration = Callable[[dict[str, Any]], dict[str, Any]]


class SchemaRegistry:
    """Register monotonic one-version migration functions by artifact kind."""

    def __init__(self) -> None:
        self._migrations: dict[tuple[str, int], Migration] = {}

    def register(self, kind: str, from_version: int, migration: Migration) -> None:
        """Register exactly one transition and reject accidental replacement."""
        if from_version < 1:
            raise ValidationError("source schema version must be positive")
        key = (kind, from_version)
        if key in self._migrations:
            raise ValidationError("migration is already registered")
        self._migrations[key] = migration

    def migrate(
        self, kind: str, payload: dict[str, Any], *, from_version: int, to_version: int
    ) -> dict[str, Any]:
        """Apply a complete forward migration chain to an independent copy."""
        if to_version < from_version:
            raise ValidationError("schema migrations cannot move backward")
        current = deepcopy(payload)
        for version in range(from_version, to_version):
            migration = self._migrations.get((kind, version))
            if migration is None:
                raise ValidationError(
                    f"missing migration for {kind} from version {version}",
                    path="$.schema_version",
                )
            current = migration(deepcopy(current))
            if not isinstance(current, dict):
                raise ValidationError("migration must return an object")
        return current

    def transitions(self, kind: str) -> tuple[tuple[int, int], ...]:
        """List registered transitions for an artifact kind."""
        return tuple(
            sorted(
                (version, version + 1)
                for item_kind, version in self._migrations
                if item_kind == kind
            )
        )
