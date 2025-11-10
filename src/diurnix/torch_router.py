"""Optional CPU Torch router trained only on synthetic fixtures."""

from __future__ import annotations

import torch

from diurnix.router import Intent, RouteResult, extract_features


class TorchRouter(torch.nn.Module):
    def __init__(self, seed: int = 0, ambiguity_band: float = 0.15) -> None:
        super().__init__()
        if ambiguity_band < 0:
            raise ValueError("ambiguity band cannot be negative")
        torch.manual_seed(seed)
        self.linear = torch.nn.Linear(8, len(Intent))
        self.ambiguity_band = ambiguity_band

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.linear(features)

    def route(self, text: str) -> RouteResult:
        features = torch.tensor(extract_features(text).values, dtype=torch.float32)
        with torch.no_grad():
            values = self(features).tolist()
        scores = {intent: round(float(values[index]), 6) for index, intent in enumerate(Intent)}
        ordered = sorted(scores, key=lambda item: (-scores[item], item.value))
        gap = scores[ordered[0]] - scores[ordered[1]]
        return RouteResult(ordered[0], scores, gap <= self.ambiguity_band)


def train_synthetic_router(
    items: tuple[tuple[str, Intent], ...], *, seed: int = 0, epochs: int = 30
) -> tuple[TorchRouter, tuple[float, ...]]:
    if not items:
        raise ValueError("training items cannot be empty")
    if epochs < 1:
        raise ValueError("epochs must be positive")
    model = TorchRouter(seed=seed)
    features = torch.tensor(
        [extract_features(text).values for text, _ in items], dtype=torch.float32
    )
    labels = torch.tensor([list(Intent).index(intent) for _, intent in items], dtype=torch.long)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.08)
    loss_function = torch.nn.CrossEntropyLoss()
    losses = []
    for _ in range(epochs):
        optimizer.zero_grad()
        loss = loss_function(model(features), labels)
        loss.backward()
        optimizer.step()
        losses.append(round(float(loss.detach()), 6))
    return model, tuple(losses)


def export_router_weights(model: TorchRouter) -> dict[str, object]:
    return {
        "schema_version": 1,
        "weight": [[round(float(value), 8) for value in row] for row in model.linear.weight],
        "bias": [round(float(value), 8) for value in model.linear.bias],
        "ambiguity_band": model.ambiguity_band,
        "synthetic_only": True,
    }


def restore_router_weights(value: dict[str, object]) -> TorchRouter:
    if value.get("schema_version") != 1 or value.get("synthetic_only") is not True:
        raise ValueError("unsupported Torch router checkpoint")
    model = TorchRouter(ambiguity_band=float(value["ambiguity_band"]))
    weight = torch.tensor(value["weight"], dtype=torch.float32)
    bias = torch.tensor(value["bias"], dtype=torch.float32)
    if weight.shape != model.linear.weight.shape or bias.shape != model.linear.bias.shape:
        raise ValueError("Torch router checkpoint shape mismatch")
    with torch.no_grad():
        model.linear.weight.copy_(weight)
        model.linear.bias.copy_(bias)
    return model


def compare_with_numpy(
    torch_router: TorchRouter, items: tuple[tuple[str, Intent], ...]
) -> dict[str, object]:
    from diurnix.router import NumpyRouter, routing_accuracy

    truth = tuple(label for _, label in items)
    numpy_predictions = tuple(NumpyRouter().route(text).intent for text, _ in items)
    torch_predictions = tuple(torch_router.route(text).intent for text, _ in items)
    return {
        "schema_version": 1,
        "sample_count": len(items),
        "synthetic": True,
        "numpy_accuracy": routing_accuracy(numpy_predictions, truth),
        "torch_accuracy": routing_accuracy(torch_predictions, truth),
    }
