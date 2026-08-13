from __future__ import annotations

import pytest

from diurnix.bench import BenchScorecard, scorecard_from_dict, scorecard_to_dict
from diurnix.errors import ValidationError


def _scorecard():
    return BenchScorecard(4, {"inbox": 1.0, "ledger": 0.8}, 0.9, True, 0, True)


def test_bench_scorecard_mapping_roundtrips() -> None:
    assert scorecard_from_dict(scorecard_to_dict(_scorecard())) == _scorecard()


def test_bench_scorecard_codec_rejects_extensions() -> None:
    encoded = scorecard_to_dict(_scorecard())
    encoded["extra"] = True
    with pytest.raises(ValidationError, match="schema"):
        scorecard_from_dict(encoded)
