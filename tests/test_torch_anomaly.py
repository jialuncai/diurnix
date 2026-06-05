from __future__ import annotations

import pytest

pytest.importorskip("torch")
pytestmark = [pytest.mark.model, pytest.mark.slow]
module = pytest.importorskip("diurnix.torch_anomaly")
train = module.train_synthetic_anomaly_classifier


def test_torch_anomaly_training_reduces_real_loss() -> None:
    features = (
        (0.1, 0.0, 0.0),
        (0.2, 0.1, 0.0),
        (0.3, 0.0, 0.1),
        (3.0, 2.5, 1.0),
        (4.0, 3.0, 1.5),
        (5.0, 4.0, 2.0),
    )
    labels = (0, 0, 0, 1, 1, 1)
    _, result = train(features, labels, seed=12, epochs=60)
    assert result.synthetic is True
    assert result.losses[-1] < result.losses[0]


def test_torch_anomaly_training_validates_rows() -> None:
    with pytest.raises(ValueError, match="aligned"):
        train((), ())
    with pytest.raises(ValueError, match="positive"):
        train(((1.0, 1.0, 1.0),), (0,), epochs=0)
