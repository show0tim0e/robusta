from pathlib import Path

import torch

from examples.datasets.download_cifar10 import PT_FILE, download_cifar10
from vl_scanner.core.providers.dataset import DatasetProvider

DATASET_PATH = Path(PT_FILE)


def _ensure_dataset_artifact() -> Path:
    regenerate = True
    if DATASET_PATH.exists():
        try:
            data = torch.load(DATASET_PATH, map_location="cpu")
            regenerate = not ("x" in data and "y" in data and isinstance(data["x"], torch.Tensor) and isinstance(data["y"], torch.Tensor) and data["x"].shape == (10000, 3, 32, 32) and data["y"].shape == (10000,))
        except Exception:
            regenerate = True

    if regenerate:
        generated_path = Path(download_cifar10())
        assert generated_path == DATASET_PATH

    assert DATASET_PATH.exists()
    return DATASET_PATH


def test_cifar10_download():
    dataset_path = _ensure_dataset_artifact()

    data = torch.load(dataset_path, map_location="cpu")
    assert "x" in data
    assert "y" in data

    x, y = DatasetProvider.load(dataset_path)
    assert isinstance(x, torch.Tensor)
    assert isinstance(y, torch.Tensor)
    assert x.shape == (10000, 3, 32, 32)
    assert y.shape == (10000,)
