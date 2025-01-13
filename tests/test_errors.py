from __future__ import annotations

from diurnix.errors import DiurnixError, IntegrityError, ValidationError


def test_base_error_preserves_stable_context() -> None:
    error = DiurnixError("stopped", context={"step": 2})
    assert str(error) == "stopped"
    assert error.as_dict() == {
        "code": "runtime_error",
        "message": "stopped",
        "context": {"step": 2},
    }


def test_validation_error_identifies_nested_path() -> None:
    assert ValidationError("missing", path="$.payload.id").as_dict()["context"] == {
        "path": "$.payload.id"
    }


def test_integrity_error_reports_both_digests() -> None:
    error = IntegrityError("mismatch", expected="aa", actual="bb")
    assert error.code == "integrity_error"
    assert error.context == {"expected": "aa", "actual": "bb"}
