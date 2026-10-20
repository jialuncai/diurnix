"""Optional CPU Torch anomaly classifier for synthetic feature rows."""

from __future__ import annotations

from dataclasses import dataclass

import torch


class TorchAnomalyClassifier(torch.nn.Module):
    def __init__(self, seed: int = 0) -> None:
        super().__init__()
        torch.manual_seed(seed)
        self.linear = torch.nn.Linear(3, 1)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        output: torch.Tensor = self.linear(features).squeeze(-1)
        return output


@dataclass(frozen=True, slots=True)
class AnomalyTrainingResult:
    losses: tuple[float, ...]
    synthetic: bool = True


def train_synthetic_anomaly_classifier(
    features: tuple[tuple[float, float, float], ...],
    labels: tuple[int, ...],
    *,
    seed: int = 0,
    epochs: int = 40,
) -> tuple[TorchAnomalyClassifier, AnomalyTrainingResult]:
    if not features or len(features) != len(labels):
        raise ValueError("anomaly training rows and labels must be nonempty and aligned")
    if epochs < 1:
        raise ValueError("anomaly training epochs must be positive")
    model = TorchAnomalyClassifier(seed)
    x = torch.tensor(features, dtype=torch.float32)
    y = torch.tensor(labels, dtype=torch.float32)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.15)
    loss_function = torch.nn.BCEWithLogitsLoss()
    losses = []
    for _ in range(epochs):
        optimizer.zero_grad()
        loss = loss_function(model(x), y)
        loss.backward()
        optimizer.step()
        losses.append(round(float(loss.detach()), 6))
    return model, AnomalyTrainingResult(tuple(losses))
