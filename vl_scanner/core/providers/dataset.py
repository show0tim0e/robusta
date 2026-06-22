from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import torch
from torch import Tensor


def _validate_dataset_payload(payload: dict[str, Any]) -> dict[str, Any]:
    required_keys = {"x", "y"}
    missing_keys = required_keys.difference(payload)
    if missing_keys:
        missing_fields = ", ".join(sorted(missing_keys))
        raise ValueError(f"Dataset payload is missing required fields: {missing_fields}.")

    x = payload["x"]
    y = payload["y"]
    if not isinstance(x, Tensor):
        raise TypeError("Dataset payload x must be a torch.Tensor.")
    if not isinstance(y, Tensor):
        raise TypeError("Dataset payload y must be a torch.Tensor.")
    if x.shape[0] != y.shape[0]:
        raise ValueError("Dataset payload x and y must have the same number of samples.")

    return payload


class DatasetProvider:
    @staticmethod
    def load(path: str | Path) -> tuple[Tensor, Tensor]:
        dataset_path = Path(path).expanduser().resolve()
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

        payload = torch.load(dataset_path, map_location="cpu")
        validated_payload = _validate_dataset_payload(payload)
        return cast(tuple[Tensor, Tensor], (validated_payload["x"], validated_payload["y"]))
